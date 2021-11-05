# This script is fetched during the kickstarted installation of machines shipping with a hypervisor.
# It is then executed once upon first-boot as a systemd-unit

# virsh command fail. would need to fetch a script and execute post-launch with a delay, for example using a systemd unit 
virsh pool-define-as iso dir - - - - /var/lib/libvirt/iso/ # Make libvirt aware of this new directory by creating a so-called 'pool'.
virsh pool-build iso # Build the pool
virsh pool-start iso # Start it
virsh pool-autostart iso # Set-it to autostart

# Create and start a new diskless VM using virt-install, but do not launch any installation

virt-install \
    --connect qemu:///system \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name my-first-live-vm \
    --boot uefi \
    --cpu host-model,topology.sockets=1,topology.cores=1,topology.threads=1 \
    --vcpus 1 \
    --memory 2048 \
    --video virtio \
    --channel spicevmc \
    --autoconsole none \
    --sound none \
    --controller type=virtio-serial \
    --controller type=usb,model=none \
    --controller type=scsi,model=virtio-scsi \
    --network network=default,model=virtio \
    --input type=keyboard,bus=virtio \
    --input type=tablet,bus=virtio \
    --rng /dev/urandom,model=virtio \
    --disk none \
    --cdrom=/var/lib/libvirt/iso/netboot.xyz.iso \
    --install no_install=yes
    
# Set the default wallpaper for Phyllome

gsettings set org.gnome.desktop.background picture-uri 'file:///usr/share/backgrounds/elementary/Morskie Oko.jpg'
