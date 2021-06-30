#            __          ____                        ____  _____
#     ____  / /_  __  __/ / /___  ____ ___  ___     / __ \/ ___/
#    / __ \/ __ \/ / / / / / __ \/ __ `__ \/ _ \   / / / /\__ \
#   / /_/ / / / / /_/ / / / /_/ / / / / / /  __/  / /_/ /___/ /
#  / .___/_/ /_/\__, /_/_/\____/_/ /_/ /_/\___/   \____//____/
# /_/          /____/

# WHAT ? This Kickstart file bootstraps a server-oriented virtual machine.
# 'v' for virtual machine, 'e' for efi, 'l' for 'lvm', 's' for server, 'd' for development.

# USAGE : Press the `tab` or 'e' key during POST and apend that after the 'quiet' string :
# inst.ks=https://git.phyllo.me/home/kickstart/raw/branch/master/f34/velsd.cfg
# A shorter URL can also be used :
# inst.ks=https://url.phyllo.me/velsd

# ATTENTION : this kickstart file will automatically DESTROY the main virtual disk 'vda' and all of its contents. 
# Bye bye!

## INSTALLATION SOURCE ##

# Configure the cdrom as the installation method
cdrom

# Set URL
url --url="http://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os"

## INSTALLATION TYPE ##

# Perform Installation in text mode
text

## REPOSITORIES ##

# Add mirro and repo
url --mirrorlist="https://mirrors.fedoraproject.org/metalink?repo=fedora-34&arch=x86_64"
repo --name=fedora-updates --mirrorlist="https://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f34&arch=x86_64" --cost=0

## USER RELATED ##

# Set the keyboard layout
keyboard --xlayouts='ch (fr)'

# Set the system language to American English
lang en_US.UTF-8

# System timezone
timezone Europe/Paris --utc # Pour Paris !

# Set dummy encrypted root password and activate the root account
rootpw --iscrypted $6$2rA58L/SQu5.xMTb$u8.zqBWE5bK1/N983qDpJEp41yg66GwQ3YVTpsRghVhNiZypWyo2Zq2Qwr2tCM3bt50mKMIgHzbPdtSq9ErPz.

# Create "test" user account and set dummy encrypted password
user --name=lukas --password=$6$wlB.n8fvumAXv3xn$clVIswjLUjb7MZoJ2JHi1zk1zmx5ViQuzbVkLYf70SDan5hdqI0tUkc89nHE8pVnHStO4mcl3c1Tk0WJvCet1. --iscrypted --gecos="lukas"

## NETWORK RELATED ##

# Deactivate the firewall
firewall --disabled

# Configure Network Interfaces
network --onboot=yes --bootproto=dhcp --hostname=vesd

# Run the Setup Agent on first boot
firstboot --enable

## DISK RELATED ##

# Only use disk labelled as vda
ignoredisk --only-use=vda

# System bootloader configuration
bootloader --location=mbr

# WARNING : Dangerous command ! Will clear the Master Boot Record 
zerombr

# Partition clearing information
clearpart --all --initlabel --drives=vda

# Disk partitioning information. 
# Will create an efi partitition of 128 MiB, a boot partition of 350 MiB on disk vda using the ext4 filesystem. The remaining space will be used for root. 
part /boot/efi --fstype="efi" --ondisk=vda --size=128 --fsoptions="umask=0077,shortname=winnt" --label=efi
part /boot --fstype="ext4" --ondisk=vda --size=350 --label=boot
part pv.122 --fstype="lvmpv" --ondisk=vda --grow
volgroup system --pesize=4096 pv.122 
logvol / --fstype="ext4" --percent 100 --label="root" --name=root --vgname=system

# System timezone
timezone Europe/Paris --utc

## SOFTWARE ##

# Install packages for the server environment. 'Core' and 'Base' are always selected 
%packages

@core
qemu-guest-agent # Install software to allow the host to better interact with the guest (can't find the spice-vdagent package)
## spice-vdagent
-fedora-logos # To be removed if we want to redistribute as Fedora Remix. 
-fedora-release-notes  # To be removed if we want to redistribute as Fedora Remix. 

%end

## POST-INSTALLATION SCRIPTS ##

%post --log=/root/ks-post.log ## Start of the %post section with logging into /root/ks-post.log

localectl set-keymap ch-fr # Set keymap to `ch-fr`. Alternatively, `us` can be picked
sed -i 's/5/1/' /etc/default/grub # set the GRUB_TIMEOUT countdown to 1 instead of 5 seconds.
grub2-mkconfig -o /boot/grub2/grub.cfg # Update grub 
reboot # Reboot the installer (doesn't work (tm))

%end # End of the %post section