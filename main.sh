#!/bin/bash
# Check if the required arguments are provided
if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Usage: $0 [-v] inputs results"
    exit 1
fi
VERBOSE=false
if [ "$1" == "-v" ]; then
    VERBOSE=true
    shift
fi
# Activate the `coffee-chats` virtual environment
source coffee-chats/bin/activate
# Run the python script with the provided arguments
if $VERBOSE; then
    python3 lib/main.py -v "$1" "$2"
else
    python3 lib/main.py "$1" "$2"
fi
# Deactivate the virtual environment
deactivate
