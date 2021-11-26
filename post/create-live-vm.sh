#!/bin/bash

# Create then shutdown a diskless virtual machine with spice and OpenGL enabled, using virt-install.
# Spice with OpenGL enabled Performs better than egl-headless with OpenGL enabled.
# Works with AMD and Intel GPUs on the host and does expect an EFI-based Linux guest. 
# The netboot.xyz ISO is attached to this virtual machine to allow network boot.

virt-install \
    --connect qemu:///session \
    --metadata description="Spice with OpenGL enabled Performs better than egl-headless with OpenGL enabled. Works with AMD and Intel GPUs on the host and does expect an EFI-based Linux guest" \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name linux-spice-gl \
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
    --network type=user,model=virtio \
    --controller type=virtio-serial \
    --controller type=usb,model=none \
    --controller type=scsi,model=virtio-scsi \
    --input type=keyboard,bus=virtio \
    --input type=tablet,bus=virtio \
    --rng /dev/urandom,model=virtio \
    --disk none \
    --cdrom=/var/lib/libvirt/iso/netboot.xyz.iso \
    --install no_install=yes

virsh destroy linux-spice-gl

# Create then shutdown a diskless virtual machine with egl-headless and OpenGL enabled, using virt-install.
# Works with all GPUs on the host including Nvidia's and does expect an EFI-based Linux guest. 
# The netboot.xyz ISO is attached to this virtual machine to allow network boot.

virt-install \
    --connect qemu:///session \
    --metadata description="Works with all GPUs on the host including Nvidia and does expect an EFI-based Linux guest" \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name linux-egl-headless-gl \
    --boot uefi \
    --cpu host-model,topology.sockets=1,topology.cores=1,topology.threads=1 \
    --vcpus 1 \
    --memory 2048 \
    --video virtio \
    --graphics spice,listen=none \
    --graphics egl-headless,gl.enable=yes \
    --channel spicevmc \
    --channel unix,target.type=virtio,target.name=org.qemu.guest_agent.0 \
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
    --disk none \
    --cdrom=/var/lib/libvirt/iso/netboot.xyz.iso \
    --install no_install=yes


virsh destroy linux-egl-headless-gl


# Create then shutdown a diskless virtual machine with SDL and OpenGL enabled, using virt-install.
# SDL with OpenGL enabled performs better than egl-headless or Spice with OpenGL enabled.
# May be able to work most GPUs on the host an EFI-based guest. 
# The netboot.xyz ISO is attached to this virtual machine to allow network boot.
# Note: doesn't work as of now

# virt-install \
#     --connect qemu:///session \
#     --metadata description="SDL with OpenGL enabled performs better than egl-headless or Spice with OpenGL enabled. May be able to work most GPUs on the host an EFI-based guest." \
#     --os-variant detect=off \
#     --virt-type kvm \
#     --arch x86_64 \
#     --machine q35 \
#     --name linux-sdl-gl \
#     --boot uefi \
#     --cpu host-model,topology.sockets=1,topology.cores=1,topology.threads=1 \
#     --vcpus 1 \
#     --memory 2048 \
#     --video virtio \
#     --graphics sdl \
#     --autoconsole none \
#     --console pty,target.type=virtio \
#     --sound none \
#     --network type=user,model=virtio \
#     --controller type=virtio-serial \
#     --controller type=usb,model=none \
#     --controller type=scsi,model=virtio-scsi \
#     --input type=keyboard,bus=virtio \
#     --input type=tablet,bus=virtio \
#     --rng /dev/urandom,model=virtio \
#     --disk none \
#     --cdrom=/var/lib/libvirt/iso/netboot.xyz.iso \
#     --install no_install=yes
# 
# virsh destroy linux-sdl-gl

# Create and start a new diskless VM using virt-install and qemu-system, but do not launch any installation
# Note: About to be deprecated 

# virt-install \
#     --connect qemu:///system \
#     --virt-type kvm \
#     --arch x86_64 \
#     --machine q35 \
#     --name my-first-live-vm \
#     --boot uefi \
#     --cpu host-model,topology.sockets=1,topology.cores=1,topology.threads=1 \
#     --vcpus 1 \
#     --memory 2048 \
#     --video virtio \
#     --channel spicevmc \
#     --autoconsole none \
#     --sound none \
#     --controller type=virtio-serial \
#     --controller type=usb,model=none \
#     --controller type=scsi,model=virtio-scsi \
#     --network network=default,model=virtio \
#     --input type=keyboard,bus=virtio \
#     --input type=tablet,bus=virtio \
#     --rng /dev/urandom,model=virtio \
#     --disk none \
#     --cdrom=/var/lib/libvirt/iso/netboot.xyz.iso \
#     --install no_install=yes