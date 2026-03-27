# Virt-manager post-installation configuration

%post --nochroot --log=/mnt/sysimage/root/vmm-post-scripts.log # Beginning of %post section

# Create a file to autostart virt-manager
cat > /mnt/sysimage/etc/xdg/autostart/virt-manager.desktop << EOF
[Desktop Entry]
Type=Application
Name=Virtual Machine Manager
Exec=virt-manager
EOF

# Modify the default virt-manager behavior for misc. options
cat >> /mnt/sysimage/usr/share/glib-2.0/schemas/org.virt-manager.virt-manager.gschema.override<< EOF

[org.virt-manager.virt-manager]
xmleditor-enabled=true
manager-window-height=600
manager-window-width=200

[org.virt-manager.virt-manager.connections]
uris=['qemu:///system', 'qemu:///session']
autoconnect=['qemu:///session']

[org.virt-manager.virt-manager.vmlist-fields]
cpu-usage=false

[org.virt-manager.virt-manager.stats]
update-interval=3
enable-disk-poll=true
enable-memory-poll=true
enable-net-poll=true

[org.virt-manager.virt-manager.console]
scaling=2
resize-guest=1
autoconnect=false

[org.virt-manager.virt-manager.details]
show-toolbar=false

[org.virt-manager.virt-manager.new-vm]
storage-format='raw'
cpu-default='host-model'
graphics-type='spice'

[org.virt-manager.virt-manager.confirm]
forcepoweroff=false
removedev=false
unapplied-dev=false

EOF

glib-compile-schemas /mnt/sysimage/usr/share/glib-2.0/schemas/

%end # End of the %post section
