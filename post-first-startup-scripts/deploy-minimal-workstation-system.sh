#!/bin/bash

# Deploy a virtual machine with `virt-install` and automatically install a minimal GNOME Shell desktop environment on a 5G disk.
# GPU and CPU agnostic configuration. 

virt-install \
    --connect qemu:///system \
    --metadata description="Spice with OpenGL. Minimal GNOME Shell environment. Based on Fedora Server 35" \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name minimal-workstation-system \
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
    --memballoon none \
    --rng /dev/urandom,model=virtio \
    --disk path=/var/lib/libvirt/images/virtual-desktop-system.img,format=raw,bus=virtio,cache=writeback,size=5 \
    --location=https://download.fedoraproject.org/pub/fedora/linux/releases/35/Everything/x86_64/os/ \
    --extra-args="inst.ks=https://raw.githubusercontent.com/PhyllomeOS/phyllomeos/main/dishes/virtual-desktop.cfg"