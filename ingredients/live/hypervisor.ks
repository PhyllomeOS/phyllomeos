# Live desktop hypervisor configuration

# Enable virtualization support in live environment
%packages
qemu-kvm
libvirt-client
virt-install
%end

%post --erroronfail
# Setup libvirt for live environment
mkdir -p /var/lib/libvirt
systemctl enable libvirtd
%end
