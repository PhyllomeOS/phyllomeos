#!/bin/bash

# This script can be run as a root user.

# Create then shutdown a diskless virtual machine with qemu-system, without any emulated display, using virt-install.
# It is designed for vfio-pci (pci-passthrough) in mind, and will work any guest systems that has drivers for the passthroughed GPU as well as paravirtualized drivers (Windows, or Linux). 
# The ISO that contains paravirtualized drivers for Windows is attached to this virtual machine. The user has to manually add the Windows ISO.

virt-install \
    --connect qemu:///system \
    --metadata description="Works with any GPUs that is binded to vfio-pci. A GPU needs to be manually attached to the VM. As it uses QEMU system, passthrough will work" \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name system-windows-vfio-pci \
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
    --cdrom /usr/share/virtio-win/virtio-win-0.1.171.iso \
    --disk none \
    --install no_install=yes

virsh destroy system-windows-vfio-pci