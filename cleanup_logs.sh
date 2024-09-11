#!/bin/bash

LOG_DIR="logs"  # Update this path with the actual logs directory inside the container

find "$LOG_DIR" -name "*.log" -type f -mtime +7 -exec rm -f {} \;

echo "$(date): Deleted log files older than 7 days from $LOG_DIR"