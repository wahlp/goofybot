#!/bin/bash

pid=$(pgrep -f "python3 src/bot.py")

if [ -n "$pid" ]; then
    echo "killing process with PID: $pid"
    kill "$pid"
else
    echo "no process found for 'python3 src/bot.py'"
fi
