#!/bin/bash

# Check if virt-manager is already installed
if command -v virt-manager &> /dev/null; then
  exit 0
fi

# Detect the Linux distribution
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    DISTRO="$ID"
else
    echo "Unable to determine Linux distribution. Exiting."
    exit 1
fi

echo "Detected distribution: $DISTRO"

# Install prerequisites based on distribution
case "$DISTRO" in
    ubuntu|debian)
        echo "Installing prerequisites for Debian/Ubuntu..."
        apt-get update
        apt-get install -y qemu-system libvirt-daemon-system virt-manager
        ;;
    fedora|rhel|centos)
        echo "Installing prerequisites for Fedora/RHEL/CentOS..."
        dnf install -y qemu-kvm libvirt virt-manager
        ;;
    arch)
        echo "Installing prerequisites for Arch Linux..."
        pacman -S --noconfirm qemu-desktop libvirt virt-manager
        ;;
    opensuse-tumbleweed)
        echo "Installing prerequisites for openSUSE Tumbleweed..."  
        zypper -n install qemu libvirt virt-manager
        ;;
    *)
        echo "Unsupported distribution: $DISTRO.  Manual installation required."
        exit 1
        ;;
esac
 