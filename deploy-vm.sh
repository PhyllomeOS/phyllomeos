#!/bin/bash

# Function to execute a script
execute_script() {
  local script_to_execute="$1"
  echo "Executing: $script_to_execute"
  "$script_to_execute" || {
    echo "Script failed: $script_to_execute"
    return 1  # Indicate failure
  }
  return 0  # Indicate success
}

# Array of scripts
scripts=(
  "./scripts/core-count.sh"
  "./scripts/system-memory.sh"
  "./scripts/deploy-distro.sh"
)

# Iterate through the scripts and execute them
for script in "${scripts[@]}"; do
  execute_script "$script"
done

echo "All scripts executed."