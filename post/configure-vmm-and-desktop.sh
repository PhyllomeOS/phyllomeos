#!/bin/bash

# This script is fetched during the kickstarted installation of machines shipping with a hypervisor.
# Ideally, this would happened during the installation process. 
# Eventually, the elements within this script will be moved to a kickstart file   
# It is then executed once upon first-boot as a systemd-unit

# Set the default wallpaper for Phyllome
gsettings set org.gnome.desktop.background picture-uri 'file:///usr/share/backgrounds/elementary/Morskie Oko.jpg'

# Virtual Machine Manager opionated configuration
# Options that aren't modified in comparaison to the default are commented out
# Modify the default virt-manager behavior for the console
gsettings set org.virt-manager.virt-manager.console resize-guest 1
gsettings set org.virt-manager.virt-manager.console scaling 2
gsettings set org.virt-manager.virt-manager.console autoconnect false
# gsettings set org.virt-manager.virt-manager.console grab-keys ''
# gsettings set org.virt-manager.virt-manager.console auto-redirect true

# Modify the default virt-manager behavior for confirmation dialogues
gsettings set org.virt-manager.virt-manager.confirm forcepoweroff false
# gsettings set org.virt-manager.virt-manager.confirm delete-storage true
gsettings set org.virt-manager.virt-manager.confirm removedev false
# gsettings set org.virt-manager.virt-manager.confirm pause false
# gsettings set org.virt-manager.virt-manager.confirm poweroff false

# Modify default values for new VMs
gsettings set org.virt-manager.virt-manager.new-vm storage-format 'raw'
gsettings set org.virt-manager.virt-manager.new-vm cpu-default 'host-model'
gsettings set org.virt-manager.virt-manager.new-vm graphics-type 'spice'

# Settings related to usage and statistics
# gsettings set org.virt-manager.virt-manager.vmlist-fields host-cpu-usage false
# gsettings set org.virt-manager.virt-manager.vmlist-fields memory-usage false
gsettings set org.virt-manager.virt-manager.vmlist-fields cpu-usage false
# gsettings set org.virt-manager.virt-manager.vmlist-fields disk-usage false
# gsettings set org.virt-manager.virt-manager.vmlist-fields network-traffic false
gsettings set org.virt-manager.virt-manager.stats enable-net-poll true
gsettings set org.virt-manager.virt-manager.stats update-interval 3
gsettings set org.virt-manager.virt-manager.stats enable-memory-poll true
gsettings set org.virt-manager.virt-manager.stats enable-disk-poll true
# gsettings set org.virt-manager.virt-manager.stats enable-cpu-poll true

# Modify the default virt-manager behavior for misc. options
gsettings set org.virt-manager.virt-manager manager-window-width 200
gsettings set org.virt-manager.virt-manager manager-window-height 500
# gsettings set org.virt-manager.virt-manager.details show-toolbar true
gsettings set org.virt-manager.virt-manager xmleditor-enabled true # enable xml edition
# gsettings set org.virt-manager.virt-manager.urls kickstarts @as []
# gsettings set org.virt-manager.virt-manager.urls containers @as []
# gsettings set org.virt-manager.virt-manager.urls isos @as []
# gsettings set org.virt-manager.virt-manager.urls urls @as []
# gsettings set org.virt-manager.virt-manager enable-libguestfs-vm-inspection true
gsettings set org.virt-manager.virt-manager.connections uris "['qemu:///system', 'qemu:///session']"
gsettings set org.virt-manager.virt-manager.connections autoconnect "['qemu:///system', 'qemu:///session']"
gsettings set org.virt-manager.virt-manager.confirm unapplied-dev false
# gsettings set org.virt-manager.virt-manager.paths screenshot-default ''
# gsettings set org.virt-manager.virt-manager.paths perms-fix-ignore @as []
# gsettings set org.virt-manager.virt-manager.paths media-default ''
# gsettings set org.virt-manager.virt-manager.paths image-default ''

