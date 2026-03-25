#!/bin/bash

# Read the total memory from /proc/meminfo in MiB
total_memory=$(awk '/MemTotal/ {print $2}' /proc/meminfo)

# Convert to MiB by dividing by 1024 (since MemTotal is in KiB)
total_memory_mb=$(( total_memory / 1024 ))

if [[ "$total_memory_mb" -lt "4096" ]]; then
    echo "Not enough RAM: The system has only ${total_memory_mb}MiB of RAM, but at least 4096 is required."
    exit 1
fi