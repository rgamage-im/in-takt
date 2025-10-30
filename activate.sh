#!/bin/bash
# Script to activate Python virtual environment
# NOTE: You must run this using 'source activate.sh' or '. activate.sh'
# Check for common virtual environment directory names
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment 'venv' activated"
elif [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Virtual environment '.venv' activated"
elif [ -d "env" ]; then
    source env/bin/activate
    echo "Virtual environment 'env' activated"
else
    echo "No virtual environment found. Please create one first:"
    echo "  python -m venv venv"
    exit 1
fi
