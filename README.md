# rofifind

**rofifind** is a fast, customizable file finder and opener using [Rofi](https://github.com/davatorium/rofi) as a graphical interface and `find` as the backend. It supports fuzzy path searching, optional hidden file visibility, command customization, and inline web search via `!bang` commands.

---

## Features

- 🔍 Search files by partial name or path using `find`
- 🧠 Background loading screen while searching
- 📂 Customizable open commands per file (e.g. open with editor, viewer, etc.)
- 📋 Copy file path to clipboard
- 🌐 Bang-commands for quick actions (`!g` for Google search, etc.)
- ⚙️ Configurable via `~/.config/rofifind/config.json`
- 🖱️ Rofi-based GUI makes it non-terminal interactive

---

## Installation

1. **Dependencies** (make sure these are installed):

    - `rofi`
    - `find`
    - `firefox` (optional, for `!g` bang)
    - `hyprctl` (optional, used to focus Firefox window)

2. **Install the script:**

   ```bash
   mkdir -p ~/.local/bin
   cp rofifind ~/.local/bin/
   chmod +x 
   ```

### Bang Commands

Type these directly into the prompt:

```
!g your search terms — Search Google in Firefox

!p /new/search/path — Change the search directory dynamically
```

### Configuration

Create a config file at:

```
~/.config/rofifind/config.json
```

Example:
```json

{
  "search_dir": "/home/yourname",
  "include_hidden": true,
  "exclude_paths": ["*/.cache/*", "*/node_modules/*"],
  "open_commands": {
    "xdg-open": "xdg-open",
    "kitty micro": "kitty -e micro",
    "copy path": "sh -c \"echo '{file}' | xclip -selection clipboard\""
  }
}
```

Config Fields:

```
search_dir: Default root path for searches.

include_hidden: Whether to include hidden files (.*).

exclude_paths: List of find-compatible patterns to skip.

open_commands: Custom openers for selected files. Use {file} as a placeholder.

```
    