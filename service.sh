#!/bin/bash

if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found"
    exit
fi

onCtrlC () {
    echo 'Ctrl+C is captured'    
}

trap 'onCtrlC' INT

nohup python3 main.py > block.log &
