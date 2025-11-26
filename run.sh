#!/bin/bash
# QuietlyStated runner script - uses the correct Python 3 interpreter

# Set MongoDB credentials
export MONGODB_URI="mongodb+srv://olasubomifemi98:onejA1Qn36Y1X6D8@labs.1xfy0.mongodb.net/quietlystated"
export MONGODB_DB_NAME="quietlystated"

# Run the CLI with python3
/usr/local/bin/python3 cli.py "$@"

