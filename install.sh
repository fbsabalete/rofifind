#!/bin/bash

set -e

SCRIPT_NAME="src/rofifind.py"
TARGET_NAME="rofifind"
BIN_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/rofifind"
CONFIG_FILE="$CONFIG_DIR/config.json"

install_rofifind() {
  echo "Installing rofifind..."

  mkdir -p "$BIN_DIR"
  cp "$SCRIPT_NAME" "$BIN_DIR/$TARGET_NAME"
  chmod +x "$BIN_DIR/$TARGET_NAME"

  mkdir -p "$CONFIG_DIR"
  if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" <<EOF
{
  "search_dir": "$HOME",
  "include_hidden": false,
  "exclude_paths": ["*/.cache/*", "*/node_modules/*"],
  "open_commands": {
    "xdg-open": "xdg-open",
    "kitty micro": "kitty -e micro",
    "copy path": "sh -c \\"echo '{file}' | xclip -selection clipboard\\""
  }
}
EOF
    echo "Created default config at $CONFIG_FILE"
  else
    echo "Config already exists at $CONFIG_FILE"
  fi

  echo "Installed $TARGET_NAME to $BIN_DIR/"
  echo "Make sure $BIN_DIR is in your PATH."
}

uninstall_rofifind() {
  echo "Uninstalling rofifind..."

  rm -f "$BIN_DIR/$TARGET_NAME"
  echo "Removed $BIN_DIR/$TARGET_NAME"

  if [ -d "$CONFIG_DIR" ]; then
    read -rp "Remove config directory at $CONFIG_DIR? [y/N]: " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
      rm -r "$CONFIG_DIR"
      echo "Removed $CONFIG_DIR"
    else
      echo "Config directory preserved."
    fi
  fi
}

# Main
case "$1" in
  uninstall)
    uninstall_rofifind
    ;;
  install|"")
    install_rofifind
    ;;
  *)
    echo "Usage: $0 [install|uninstall]"
    exit 1
    ;;
esac
