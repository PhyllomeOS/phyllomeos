#!/bin/bash

# Default values
DEFAULT_MEMORY=4096
DEFAULT_DISK_SIZE=10

# Prompt user for VM memory size
read -r -p "Provide desired VM memory in MB or press Enter to keep default value of $DEFAULT_MEMORY MB): " memory_size
memory_size=${memory_size:-$DEFAULT_MEMORY}

# Validate memory size
if ! [[ "$memory_size" =~ ^[0-9]+$ ]] || (( memory_size < 2048 )); then
    echo "Invalid memory size.  Must be a number greater than or equal to 2048. Using default value of $DEFAULT_MEMORY MB."
    memory_size=$DEFAULT_MEMORY
fi

# Prompt user for VM disk size
read -r -p "Provide desired disk size of VM in GB or press Enter to use default disk size of $DEFAULT_DISK_SIZE GB: " disk_size
disk_size=${disk_size:-$DEFAULT_DISK_SIZE}

# Validate disk size
if ! [[ "$disk_size" =~ ^[0-9]+$ ]] || (( disk_size < 10 )); then
    echo "Invalid disk size.  Must be a number greater than or equal to 10 GiB. Using default value of $DEFAULT_DISK_SIZE."
    disk_size=$DEFAULT_DISK_SIZE
fi

# Set the choices
CHOICE_SYSTEM="qemu:///system"
CHOICE_SESSION="qemu:///session"

# Display the choices to the user
echo "Please select an option or press Enter to keep default value of $CHOICE_SESSION):"
echo "1) $CHOICE_SYSTEM (system-based or rootfull virtual machine)"
echo "2) $CHOICE_SESSION (session-based or rootless virtual machine)"

# Prompt the user for input
IFS= read -r -p "Enter your choice (1 or 2): " user_choice

# Validate the user's input
if [[ ! "$user_choice" =~ ^[12]$ ]]; then
  echo "Invalid choice.  Defaulting to session-based VM."
  uri="$CHOICE_SESSION"  # Default to session-based if input is invalid
else
  # Determine the selected option
  case "$user_choice" in
    1)
      uri="$CHOICE_SYSTEM"
      ;;
    2)
      uri="$CHOICE_SESSION"
      ;;
    *)
      echo "Unexpected error: Invalid choice. This should not happen due to validation."
      exit 1
      ;;
  esac

  # Conditional variable assignment based on URI
  if [[ "$uri" == "qemu:///system" ]]; then
    disk_path="/var/lib/libvirt/images/"
    network_type="default"
  elif [[ "$uri" == "qemu:///session" ]]; then
    disk_path="$HOME/.local/share/libvirt/images/"
    network_type="user"
  fi
fi

# Display the selected option (optional)
echo "You selected: $uri"

# Get a list of files in "dishes" directory
mapfile -t dish_name < <(find "dishes/" -maxdepth 1 -type f \( -name "virtual*" \) -printf "%f\n" | sed 's/\.[^.]*$//')

# Check if there are any files
if [ ${#dish_name[@]} -eq 0 ]; then
  echo "No files found in the directory ../dishes."
  exit 1
fi

# Display the files with numbered options
echo "Available files:"
for i in "${!dish_name[@]}"; do
  echo "$((i + 1)). ${dish_name[$i]}"
done

# Prompt the user to select a file
read -r -p "Enter the number of the file you want to select: " choice

# Validate the user's choice
if ! [[ "$choice" =~ ^[0-9]+$ ]] || (( choice < 1 )) || (( choice > ${#dish_name[@]} )); then
  echo "Invalid choice. Please enter a number from 1 to ${#dish_name[@]}."
  exit 1
fi

# Get the selected filename
vm_name="${dish_name[$((choice - 1))]}"

# Output the selected filename
echo "You selected: $vm_name"

# virt-install command with user-defined VM name
virt-install \
    --connect "$uri" \
    --os-variant fedora41 \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name "$vm_name" \
    --boot uefi \
    --cpu host-model,topology.sockets=1,topology.cores=2,topology.threads=2 \
    --vcpus 4 \
    --memory "$memory_size" \
    --video virtio \
    --channel unix,target.type=virtio,target.name=org.qemu.guest_agent.0 \
    --autoconsole none \
    --console pty,target.type=virtio \
    --sound virtio \
    --network type="$network_type",model=virtio \
    --controller type=virtio-serial \
    --controller type=usb,model=none \
    --controller type=scsi,model=virtio-scsi \
    --input type=keyboard,bus=virtio \
    --input type=mouse,bus=virtio \
    --rng /dev/urandom,model=virtio \
    --iommu model=virtio \
    --memballoon none \
    --disk path="${disk_path}/${vm_name}.img",format=raw,bus=virtio,cache=writeback,size="$disk_size" \
    --location=https://download.fedoraproject.org/pub/fedora/linux/releases/42/Everything/x86_64/os/ \
    --initrd-inject ./dishes/"$vm_name".cfg \
    --extra-args "inst.ks=file:/$vm_name.cfg" 

echo "virt-install command executed with VM name: $vm_name"