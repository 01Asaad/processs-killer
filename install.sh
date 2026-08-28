#!/usr/bin/env bash

NAME="killer"

set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PREFIX_DIR="${PREFIX:-"$HOME/.local"}"
INSTALL_DIR="$PREFIX_DIR/lib/$NAME"
BIN_DIR="$PREFIX_DIR/bin"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required but was not found." >&2
    exit 1
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR"
install -m 644 \
    "$SCRIPT_DIR/main.py" \
    "$SCRIPT_DIR/Line.py" \
    "$INSTALL_DIR/"

LAUNCHER="$BIN_DIR/$NAME"
rm -f "$LAUNCHER"
cat >"$LAUNCHER" <<EOF
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/main.py" "\$@"
EOF
chmod 755 "$LAUNCHER"

echo "Installed $NAME to $LAUNCHER"

case ":${PATH:-}:" in
    *:"$BIN_DIR":*) ;;
    *) echo "Add $BIN_DIR to your PATH to run '$NAME' from anywhere." ;;
esac
