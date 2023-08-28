#!/bin/bash

cd src
nohup python3 bot.py >> ../logs/nohup.out 2>&1 &
echo "starting bot..."

