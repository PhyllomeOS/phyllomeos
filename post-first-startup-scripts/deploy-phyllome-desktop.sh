#!/bin/bash

# Deploy Phyllome OS Desktop generic edition  with `virt-install` on a 20G disk, with 4vCPU, 8G of RAM.
# GPU and CPU agnostic configuration. 

virt-install \
    --connect qemu:///system \
    --metadata description="Spice with OpenGL. Phyllome OS Desktop edition." \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name virtual-phyllome-os \
    --boot uefi \
    --cpu host-passthrough,topology.sockets=1,topology.cores=2,topology.threads=2 \
    --vcpus 4 \
    --memory 4092 \
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
    --disk path=/var/lib/libvirt/images/virtual-phyllome-os.img,format=raw,bus=virtio,cache=writeback,size=20 \
    --location=https://download.fedoraproject.org/pub/fedora/linux/releases/35/Everything/x86_64/os/ \
    --extra-args="inst.ks=https://raw.githubusercontent.com/PhyllomeOS/phyllomeos/main/dishes/virtual-phyllome-desktop.cfg"