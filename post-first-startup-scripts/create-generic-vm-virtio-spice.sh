#!/bin/bash

# This script has be run as root.

# Create and run a diskless virtual machine with `virt-install`. Spice and OpenGL are enabled.
# GPU agnostic configuration. Does expect an EFI-based Linux guest. 
# The netboot.xyz ISO is attached to this virtual machine, allowing the user to pick an operating system to be installed.

virt-install \
    --connect qemu:///system \
    --metadata description="Spice with OpenGL. Requires an EFI-based guest, ideally with support for virtio-gpu, such as Fedora Workstation." \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name generic \
    --boot uefi \
    --cpu host-model,topology.sockets=1,topology.cores=1,topology.threads=1 \
    --vcpus 1 \
    --memory 2048 \
    --video virtio \
    --graphics spice,gl.enable=yes,listen=none \
    --channel spicevmc \
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
    --cdrom /var/lib/libvirt/iso/netboot.xyz.iso \
    --memballoon none \
    --rng /dev/urandom,model=virtio \
    --disk none \
    --install no_install=yes