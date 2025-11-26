#!/bin/bash
# QuietlyStated runner script - uses the correct Python 3 interpreter

# Set MongoDB credentials
export MONGODB_URI=
export MONGODB_DB_NAME=

# Run the CLI with python3
/usr/local/bin/python3 cli.py "$@"

