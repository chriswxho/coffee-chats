#!/bin/bash
# Check if the required arguments are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <inputs> <results>"
    exit 1
fi
# Activate the virtual environment
source coffee-chats/bin/activate
# Run the python script with the provided arguments
python3 main.py "$1" "$2"
# Deactivate the virtual environment
deactivate
