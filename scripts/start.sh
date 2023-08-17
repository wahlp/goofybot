#!/bin/bash

nohup python3 src/bot.py > logs/nohup.out 2>&1 &
echo "starting bot..."

