import subprocess
import re

# Get all package names from your config file
packages = []
with open('core-packages-hardware-support.cfg', 'r') as f:
    for line in f:
        if line.strip() and not line.startswith('#') and '#' not in line:
            # Extract package name (everything before the first space or #)
            package = line.strip().split('#')[0].strip()
            if package and not package.startswith('%'):
                packages.append(package)

# Get summaries using dnf info
summaries = {}
for package in packages:
    try:
        result = subprocess.run(['dnf', 'info', package], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            # Extract summary line
            summary_match = re.search(r'Summary\s*:\s*(.+)', result.stdout)
            if summary_match:
                summaries[package] = summary_match.group(1).strip()
    except Exception as e:
        print(f"Error getting info for {package}: {e}")

# Now you can generate your updated package list with summaries
with open('core-packages-hardware-support.cfg', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip() and not line.startswith('#') and not line.startswith('%'):
        package = line.strip().split('#')[0].strip()
        if package in summaries:
            line = f"{package} # {summaries[package]}\n"
    new_lines.append(line)

# Write back to file (or save as new file)
with open('updated-packages.cfg', 'w') as f:
    f.writelines(new_lines)
