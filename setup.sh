#!/bin/bash
python3 -m venv coffee-chats
# Activate the virtual environment
source coffee-chats/bin/activate
pip install -r requirements.txt
deactivate
