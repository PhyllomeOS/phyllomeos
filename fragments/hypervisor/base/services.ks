# Hypervisor base configuration

services --enabled="NetworkManager,systemd-resolved,libvirtd" # Without libvirtd here, it appears the service won't automatically start
