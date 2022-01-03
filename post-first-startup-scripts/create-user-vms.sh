#!/bin/bash

# This script can be run as a normal user.
# Make sure qemu-session is available as an URI in virt-manager running the following in your terminal: 
# gsettings set org.virt-manager.virt-manager.connections uris "['qemu:///system', 'qemu:///session']"
# gsettings set org.virt-manager.virt-manager.connections autoconnect "['qemu:///system', 'qemu:///session']"


# Create then shutdown a diskless virtual machine with qemu-session, a spice display without 3D acceleration, using virt-install.
# Works with any GPUs on the host but does not provide 3D acceleration. Does expect an EFI-based Linux guest. 
# No ISO is attached to this virtual machine. The user have to manually add one.

virt-install \
    --connect qemu:///session \
    --metadata description="Works with any GPUs on the host but does not provide 3D acceleration. Does expect an EFI-based Linux guest. As it uses QEMU session, passthrough wont work out of the box" \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name user-linux-spice \
    --boot uefi \
    --cpu host-model,topology.sockets=1,topology.cores=1,topology.threads=1 \
    --vcpus 1 \
    --memory 2048 \
    --video virtio \
    --graphics spice,listen=none \
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
    --install no_install=yes

virsh destroy user-linux-spice

# Create then shutdown a diskless virtual machine with qemu-session, spice and opengl enabled, using virt-install.
# Spice with OpenGL performs better than egl-headless.
# Works with AMD and Intel GPUs on the host and does expect an EFI-based Linux guest. 
# No ISO is attached to this virtual machine. The user have to manually add one.

virt-install \
    --connect qemu:///session \
    --metadata description="Spice with OpenGL enabled performs better than egl-headless with OpenGL enabled. Works with AMD and Intel GPUs on the host and does expect an EFI-based Linux guest. As it uses QEMU session, passthrough wont work out of the box" \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name user-linux-spice-gl \
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
    --install no_install=yes

virsh destroy user-linux-spice-gl

# Create then shutdown a diskless virtual machine with qemu-sesssion, egl-headless and opengl enabled, using virt-install.
# Works with all GPUs on the host including Nvidia's and does expect an EFI-based Linux guest. 
# No ISO is attached to this virtual machine. The user have to manually add one.

virt-install \
    --connect qemu:///session \
    --metadata description="Works with all GPUs on the host including Nvidia and does expect an EFI-based Linux guest. As it uses QEMU session, passthrough wont work out of the box" \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name user-linux-egl-headless-gl \
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
    --install no_install=yes

virsh destroy user-linux-egl-headless-gl

# Create then shutdown a diskless virtual machine with qemu-sesssion, SDL and OpenGL enabled, using virt-install.
# Should work with all GPUs on the host including Nvidia's and does expect an EFI-based Linux guest. 
# No ISO is attached to this virtual machine. The user have to manually add one.

virt-install \
    --connect qemu:///session \
    --metadata description="SDL with OpenGL enabled performs better than egl-headless or Spice with OpenGL enabled. Should work with most GPUs. As it uses QEMU session, passthrough wont work out of the box" \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name linux-sdl-gl \
    --boot uefi \
    --cpu host-model,topology.sockets=1,topology.cores=1,topology.threads=1 \
    --vcpus 1 \
    --memory 2048 \
    --video virtio \
    --graphics sdl \
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
    --install no_install=yes

virsh destroy user-linux-sdl-gl