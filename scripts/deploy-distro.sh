#!/bin/bash

# Get a list of files in the directory dishes without extensions
mapfile -t dish_name < <(find "dishes/" -maxdepth 1 -type f -printf "%f\n" | sed 's/\.[^.]*$//')

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
    --connect qemu:///system \
    --os-variant fedora41 \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name "$vm_name" \
    --boot uefi \
    --cpu host-model,topology.sockets=1,topology.cores=2,topology.threads=1 \
    --vcpus 2 \
    --memory 2048 \
    --video virtio \
    --autoconsole none \
    --console pty,target.type=virtio \
    --sound none \
    --network type=user,model=virtio \
    --controller type=virtio-serial \
    --controller type=usb,model=none \
    --controller type=scsi,model=virtio-scsi \
    --input type=keyboard,bus=virtio \
    --input type=tablet,bus=virtio \
    --rng /dev/urandom,model=virtio \
    --disk path=/var/lib/libvirt/images/"$vm_name".img,format=raw,bus=virtio,cache=writeback,size=10 \
    --location=https://download.fedoraproject.org/pub/fedora/linux/releases/42/Everything/x86_64/os/ \
    --initrd-inject "./dishes/$vm_name".cfg \
    --extra-args "inst.ks=file:$vm_name.cfg"

echo "virt-install command executed with VM name: $vm_name"