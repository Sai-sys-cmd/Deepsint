#!/bin/bash

# Script to find Blackbird in PATH and execute it with a username
# Usage: ./run_blackbird.sh <username>

USERNAME="$1"

if [ -z "$USERNAME" ]; then
    echo "Error: No username provided"
    echo "Usage: $0 <username>"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Try to find blackbird in various locations
BLACKBIRD_PATH=""

# First, try local installation in blackbird subdirectory
if [ -f "$SCRIPT_DIR/blackbird/blackbird.py" ]; then
    BLACKBIRD_PATH="python3 $SCRIPT_DIR/blackbird/blackbird.py"
    echo "Found local Blackbird installation"
# Try to find blackbird in PATH
elif command -v blackbird >/dev/null 2>&1; then
    BLACKBIRD_PATH="blackbird"
    echo "Found Blackbird in PATH"
# Try blackbird.py in PATH
elif command -v blackbird.py >/dev/null 2>&1; then
    BLACKBIRD_PATH="blackbird.py"
    echo "Found blackbird.py in PATH"
# Try python module
elif python3 -c "import blackbird" 2>/dev/null; then
    BLACKBIRD_PATH="python3 -m blackbird"
    echo "Found Blackbird as Python module"
else
    echo "Error: Blackbird not found"
    echo "Please ensure Blackbird is installed"
    exit 1
fi

echo "Searching for username: $USERNAME"

# Execute Blackbird with the provided username and JSON output
$BLACKBIRD_PATH --username "$USERNAME" --json --no-update

exit $?
