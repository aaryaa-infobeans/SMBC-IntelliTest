#!/usr/bin/env bash
 
##################################################################################################
# This script is used to set appropriate PYTHONPATH environment variable to load pylibs and
# also loads environment variable from .env file
# Usage: ./pyRunner.sh <python_script_path>
##################################################################################################
 
# Check if file path is provided as an argument.
if [ $# -eq 0 ]; then
    echo ""
    echo "Usage: ./$(basename $0) <python_script_path>"
    echo ""
    exit 1
fi
 
current_dir=$(pwd)
script_dir=$(realpath $(dirname "$0"))
parent_dir=$(dirname "$script_dir")
 
# Load environment vairable from .env file
if [ -f .env ]; then
    set -a
    source .env
    set +a
elif [ -f "$script_dir/.env" ]; then
    set -a
    source "$script_dir/.env"
    set +a
else
    echo ""
    echo "Warning: Cannot find .env file in current or script's directory."
    echo ""
fi
 
 
#Set PYTHONPATH environment variable
export PYTHONPATH=$PROJECT_DIR
 
# Run python command with the command line arguments.
set -x
python "$@"
 
 