# VMM post-installation scripts

%post --erroronfail

# Start libvirt service
systemctl enable libvirtd
systemctl start libvirtd

%end
