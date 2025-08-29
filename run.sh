#!/bin/bash

# Get current timestamp
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")

# Log file name
logfile="run_${timestamp}.log"

# Run the Python script with all arguments, append output to logs
python src/main.py "$@" >> "logs/$logfile" 2>&1

wait 30

# Run evaluation of the metrics
python src/tracer_agent.py

echo "Run complete. Logs saved to $logfile"
