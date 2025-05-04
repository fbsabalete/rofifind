#!/usr/bin/env python3
import subprocess
import os
import sys
import shlex
import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "rofifind" / "config.json"

# Defaults
search_dir = os.path.expanduser("~")
include_hidden = False
default_commands = {
    "xdg-open": "xdg-open",
    "kitty micro": "kitty -e micro",
    "copy path": "sh -c \"echo '{file}' | xclip -selection clipboard\"",
}


def load_config():
    """Load user-defined commands from config file if it exists."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            try:
                data = json.load(f)
                return data.get("open_commands", default_commands)
            except json.JSONDecodeError:
                pass
    return default_commands


def rofi_menu(prompt, options, allow_custom=False):
    args = ["rofi", "-dmenu", "-p", prompt]
    if allow_custom:
        args.append("-editable")
    rofi = subprocess.Popen(
        args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    input_data = "\n".join(options).encode("utf-8")
    stdout, _ = rofi.communicate(input=input_data)
    return stdout.decode("utf-8").strip()


def build_find_command(query, hidden):
    cmd = ["find", search_dir]
    if not hidden:
        cmd += ["-not", "-path", "*/.*"]
    cmd += ["-iname", f"*{query}*"]
    return cmd


def expand_command(template, file_path):
    if "{file}" in template:
        return template.replace("{file}", shlex.quote(file_path))
    else:
        return template + " " + shlex.quote(file_path)


def handle_open(file_path, commands):
    """Prompt user to pick or type a command to open the file."""
    options = list(commands.keys()) + ["custom...", "cancel"]
    choice = rofi_menu("Open with:", options, allow_custom=True)

    if choice == "cancel" or not choice:
        return

    if choice in commands:
        command_str = commands[choice]
    else:
        command_str = choice  # custom command typed

    full_command = expand_command(command_str, file_path)
    subprocess.Popen(full_command, shell=True)


def main():
    global include_hidden
    commands = load_config()

    while True:
        user_input = rofi_menu("Find file (!hidden to toggle):", [], allow_custom=True)
        if not user_input:
            sys.exit(0)

        if user_input.strip() == "!hidden":
            include_hidden = not include_hidden
            rofi_menu("Hidden search", [f"Now {'ON' if include_hidden else 'OFF'}"])
            continue

        find_cmd = build_find_command(user_input, include_hidden)
        try:
            result = subprocess.check_output(
                find_cmd, stderr=subprocess.DEVNULL
            ).decode("utf-8")
            matches = (
                result.strip().split("\n") if result.strip() else ["No matches found"]
            )
        except subprocess.CalledProcessError:
            matches = ["Error running find"]

        selection = rofi_menu("Results:", matches)
        if selection and os.path.exists(selection):
            handle_open(selection, commands)


if __name__ == "__main__":
    main()
