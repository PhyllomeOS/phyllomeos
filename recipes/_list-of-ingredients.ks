#            __          ____                        ____  _____
#     ____  / /_  __  __/ / /___  ____ ___  ___     / __ \/ ___/
#    / __ \/ __ \/ / / / / / __ \/ __ `__ \/ _ \   / / / /\__ \
#   / /_/ / / / / /_/ / / / /_/ / / / / / /  __/  / /_/ /___/ /
#  / .___/_/ /_/\__, /_/_/\____/_/ /_/ /_/\___/   \____//____/
# /_/          /____/

# The list of ingredients for composing Phyllome OS
# Uncomment lines with "%include" to enable ingredient

# Installation method
# Exactly one option has to be picked
# %include ../ingredients/core.cfg # Text mode
# %include ../ingredients/live-core.cfg # For live systems only
# Documentation: https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#graphical-or-text-or-cmdline

# Storage configuration 
# Exactly one option has to be picked
# WARNING !!! Will erase local disks!
# %include ../ingredients/core-storage.cfg # Basic ext4 partition layout for UEFI-based systems
# %include ../ingredients/live-core-storage.cfg # For live systems only
# Documentation: https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#part-or-partition

# Booloader configuration
# Exactly one option has to be picked
# %include ../ingredients/core-bootloader-grub.cfg # GNU GRUB bootloader
# %include ../ingredients/core-bootloader-systemd-boot.cfg # systemd-boot, an EFI-only bootloader 
# %include ../ingredients/live-core-bootloader-grub.cfg # GNU GRUB for live systems
# Documentation: https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#bootloader

# System locale configuration
# Exactly one option has to be picked
# %include ../ingredients/core-locale.cfg # System locale sets to Swiss French as keyboard layout and English as language. Timezone is also set. Can be changed during by end-user during first boot

# Security mode 
# Exactly one option has to be picked
# %include ../ingredients/core-security-off.cfg # Sets security to low
# %include ../ingredients/core-security-on.cfg # Sets security to medium

# System services 
# Optional
# %include ../ingredients/core-services.cfg # List of systemd services that are explicitly enabled

# Network configuration
# %include ../ingredients/core-network.cfg # Network configuration
# Documentation: https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#id123

# Repositories 
# Exactly one option has to be picked
# %include ../ingredients/core-fedora-repo.cfg # Official repositories for Fedora
# %include ../ingredients/core-fedora-repo-rawhide.cfg # Official repositories for Fedora Rawhide

# Packages 
# Exactly one option has to be picked
# %include ../ingredients/core-packages-mandatory.cfg # Mandatory packages
# %include ../ingredients/core-packages-mandatory-trimming-attempt.cfg # Trimming attempt for the mandatory packages
# Mandatory packages for live editions
# %include ../ingredients/live-core-mandatory-packages.cfg # For live systems
# Other optional packages
# Recommended but not strictly required
# %include ../ingredients/core-packages-default.cfg # Recommended extra packages
# %include ../ingredients/core-packages-hardware-support.cfg # Extended hardware support. Recommended for non-virtual systems
# Documentation: https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#chapter-9-package-selection

# Pre and post installation sections. 
# Optionnal 
# All options can be picked
# %include ../ingredients/pre.cfg # Triggered just after the kickstart file has been parsed
# Documentation: https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#chapter-4-pre-installation-script
# %include ../ingredients/pre-install.cfg # Script triggered just after the system storage has been set up
# Documentation: https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#chapter-5-pre-install-script
# %include ../ingredients/core-post-nochroot.cfg # Triggered after the installation no chroot
# Documentation: https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#chapter-6-post-installation-script
# %include ../ingredients/core-post.cfg # Triggered after the installation
# Documentation: https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#chapter-6-post-installation-script
# Two options have to be picked, for live systems only
# %include ../ingredients/live-core-post.cfg # Post configuration script for a live system only
# %include ../ingredients/live-core-post-live-session.cfg # Live session script

# OEM setup
# Exactly one option has to be picked
# %include ../ingredients/core-desktop-initial-setup.cfg # Ensures that GNOME initial setup will launch on the first system start-up
# %include ../ingredients/core-server-initial-setup.cfg # For headless systems

# A GNOME Shell-based desktop environment. 
# Optionnal
# %include ../ingredients/base-desktop-gnome.cfg # A GNOME Shell-based desktop environment
# Documentation: https://fedoraproject.org/wiki/InitialSetup

# Virtualization-related packages
# Optionnal
# %include ../ingredients/base-desktop-virtual-machine-manager.cfg # Virtual Machine Manager
# %include ../ingredients/base-hypervisor.cfg # Generic building block to build a virtualization host

# Virtualization-related options
# Optionnal
# %include ../ingredients/base-hypervisor-amdcpu.cfg # Virtualization configuration for AMD (tm) CPUs
# %include ../ingredients/base-hypervisor-intelcpu.cfg # Virtualization configuration for Intel (tm) CPUs
# %include ../ingredients/base-hypervisor-intelgpu.cfg # Virtualization configuration for Intel (tm) GPUs from 4th to the 9th generation (compatible with vfio-mdev)
# %include ../ingredients/base-guest-agents.cfg # Guest agents