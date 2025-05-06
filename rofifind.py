#!/usr/bin/env python3
import subprocess
import os
import sys
import shlex
import json
import threading
import time
from pathlib import Path
from subprocess import Popen

CONFIG_PATH = Path.home() / ".config" / "rofifind" / "config.json"

# Defaults
search_dir = os.path.expanduser("~")
include_hidden = False
commands = {
    "xdg-open": "xdg-open",
    "kitty micro": "kitty -e micro",
    "copy path": "sh -c \"echo '{file}' | xclip -selection clipboard\"",
}
exclude_paths = []
loading_proc: Popen[str] = None


def load_config():
    global commands
    global include_hidden
    global search_dir
    global exclude_paths
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                data = json.load(f)
                commands = data.get("open_commands", commands)
                include_hidden = data.get("include_hidden", include_hidden)
                search_dir = data.get("search_dir", os.path.expanduser(search_dir))
                exclude_paths = data.get("exclude_paths", exclude_paths)
        except json.JSONDecodeError:
            pass


def rofi_menu(prompt, options, message="", allow_custom=False, custom_args=None):
    if custom_args is None:
        custom_args = []
    args = ["rofi", "-dmenu", "-p", prompt] + custom_args
    if message:
        args += ["-mesg", message]
    if allow_custom:
        args.append("-editable")
    rofi = subprocess.Popen(
        args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    input_data = "\n".join(options).encode("utf-8")
    stdout, _ = rofi.communicate(input=input_data)
    return stdout.decode("utf-8").strip()


def find_matches_with_loading(query):
    t = threading.Thread(target=rofi_loading)
    t.start()

    try:
        matches = find_partial_matches(query)  # Your slow function
    finally:
        t.join()

        if loading_proc and loading_proc.poll() is None:
            loading_proc.terminate()
            try:
                loading_proc.wait(timeout=0.2)
            except subprocess.TimeoutExpired:
                loading_proc.kill()

    return matches


def find_partial_matches(query):
    if not query:
        return []

    find_cmd = ["find", search_dir, "-type", "f"]
    if not include_hidden:
        find_cmd += ["!", "-path", "*/.*"]

    for excluded in exclude_paths:
        find_cmd += ["!", "-path", excluded]

    if "/" in query:
        # Treat as path: absolute or relative
        path_pattern = query if query.startswith("/") else f"*/{query}"
        find_cmd += ["-path", f"*{path_pattern}*"]
    else:
        # Treat as filename
        find_cmd += ["-iname", f"*{query}*"]

    try:
        result = subprocess.run(
            find_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        return [line for line in result.stdout.strip().split("\n") if line.strip()]
    except subprocess.CalledProcessError:
        return []


def expand_command(template, file_path):
    if "{file}" in template:
        return template.replace("{file}", shlex.quote(file_path))
    else:
        return template + " " + shlex.quote(file_path)


def handle_open(file_path, commands):
    options = list(commands.keys()) + ["Cancel"]
    choice = rofi_menu("Open with:", options, allow_custom=True)

    if choice == "cancel" or not choice:
        return

    command_str = commands.get(choice, choice)
    full_command = expand_command(command_str, file_path)
    subprocess.Popen(full_command, shell=True)
    sys.exit(0)


def web_search(query):
    subprocess.call(["firefox", "--new-tab", f"http://google.com/search?q={query}"])
    subprocess.call(["hyprctl", "dispatch", "focuswindow", "class:org.mozilla.firefox"])
    sys.exit(0)


def handle_bang(query):
    global search_dir
    if query.startswith("!p"):
        search_dir = os.path.expanduser(query.split(" ")[1:])
        return True
    if query.startswith("!g"):
        web_search(' '.join(query.split(" ")[1:]))

    return False


def rofi_loading():
    global loading_proc
    text = f"Loading..."
    loading_proc = subprocess.Popen(
        ["rofi", "-dmenu", "-p", text, "-theme-str", "#window { height: 60px; }"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True
    )


def main():
    load_config()

    while True:

        query = rofi_menu(
            f"{search_dir}",
            [],
            allow_custom=True,
            custom_args=["-theme-str", "#window { height: 60px;}"]
        )

        if not query:
            sys.exit(0)

        is_configuration = handle_bang(query)
        if is_configuration:
            continue

        matches = find_matches_with_loading(query)
        if not matches:
            matches = ["No matches found"]

        selection = rofi_menu(prompt="Results", options=matches)
        if selection and os.path.exists(selection):
            handle_open(selection, commands)


if __name__ == "__main__":
    main()
