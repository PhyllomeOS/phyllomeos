#            __          ____                        ____  _____
#     ____  / /_  __  __/ / /___  ____ ___  ___     / __ \/ ___/
#    / __ \/ __ \/ / / / / / __ \/ __ `__ \/ _ \   / / / /\__ \
#   / /_/ / / / / /_/ / / / /_/ / / / / / /  __/  / /_/ /___/ /
#  / .___/_/ /_/\__, /_/_/\____/_/ /_/ /_/\___/   \____//____/
# /_/          /____/

# Virtualization packages

%packages --exclude-weakdeps # Beginning of the packages section. Does not include weak dependencies.

qemu-kvm # QEMU metapackage for KVM support
libvirt # Library providing a simple virtualization API
libvirt-client # Client side utilities of the libvirt library
libvirt-client-qemu # Additional client side utilities for QEMU. Used to interact with some QEMU specific features of libvirt.
libvirt-daemon # Server side daemon and supporting files for libvirt library
libvirt-daemon-common # Miscellaneous files and utilities used by other libvirt daemons
libvirt-daemon-config-network # Default configuration files for the libvirtd daemon. Provides NAT based networking
libvirt-daemon-driver-interface # Interface driver plugin for the libvirtd daemon
libvirt-daemon-driver-network # The network driver plugin for the libvirtd daemon, providing an implementation of the virtual network APIs using the Linux bridge capabilities.
libvirt-daemon-driver-qemu # QEMU driver plugin for the libvirtd daemon
libvirt-daemon-kvm # Server side daemon & driver required to run KVM guests
libvirt-daemon-log # Server side daemon for managing logs
libvirt-daemon-qemu # Server side daemon and driver required to manage the virtualization capabilities of the QEMU TCG emulators
libvirt-nss # Libvirt plugin for Name Service Switch
libvirt-dbus # libvirt D-Bus API binding
libvirt-daemon-driver-ch # Cloud-Hypervisor driver plugin for libvirtd daemon
virt-install # Utilities for installing virtual machines

%end # End of the packages section
