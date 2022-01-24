#!/bin/bash

# usermod -a -G libvirt kvm $(whoami) # add current user to the libvirt and kvm groups

# virsh commands fail in a kickstart environment (chroot or not it seems). would need to fetch a script and execute post-launch with a delay, for example using a systemd unit 
virsh pool-define-as iso dir - - - - /var/lib/libvirt/iso/ # Make libvirt aware of this new directory by creating a so-called 'pool'.
virsh pool-build iso # Build the pool
virsh pool-start iso # Start it
virsh pool-autostart iso # Set-it to autostart