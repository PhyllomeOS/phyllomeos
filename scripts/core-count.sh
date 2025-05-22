#!/bin/bash

# Get the core count using nproc --all
core_count=$(nproc --all)

# Check if nproc --all returns a numerical value greater than 2
if (( core_count > 2 )); then
 echo "System has more than 2 core (nproc --all: $core_count)."
else
  echo "Warning: System has only $core_count core)."
  echo "The script requires at least four cores"
  exit 1  # Exit with an error code to indicate the condition is not met
fi
