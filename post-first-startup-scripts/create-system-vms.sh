#!/bin/bash

# Attention please: will soon be deprecated in favor of a more generic VM model 

# This script has be run as root.

# Create and run a diskless virtual machine with `virt-install`, without any display.
# For Windows, the user has to manually add the Windows ISO as well as the ISO that contains paravirtualized drivers for Windows. 

virt-install \
    --connect qemu:///system \
    --metadata description="Works with any GPUs that is binded to vfio-pci. A GPU needs to be manually attached to the VM. As it uses QEMU system, passthrough will work" \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name vfio-pci \
    --boot uefi \
    --cpu host-model,topology.sockets=1,topology.cores=1,topology.threads=1 \
    --vcpus 1 \
    --memory 2048 \
    --video none \
    --graphics none \
    --channel unix,target.type=virtio,target.name=org.qemu.guest_agent.0 \
    --autoconsole none \
    --console pty,target.type=virtio \
    --sound none \
    --network type=default,model=virtio \
    --controller type=virtio-serial \
    --controller type=usb,model=none \
    --controller type=scsi,model=virtio-scsi \
    --input type=keyboard,bus=virtio \
    --input type=tablet,bus=virtio \
    --rng /dev/urandom,model=virtio \
    --disk none \
    --install no_install=yes