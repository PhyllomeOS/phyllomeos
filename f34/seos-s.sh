#!/bin/bash

#     ____  / /_  __  __/ / /___  ____ ___  ___     / __ \/ ___/
#    / __ \/ __ \/ / / / / / __ \/ __ `__ \/ _ \   / / / /\__ \
#   / /_/ / / / / /_/ / / / /_/ / / / / / /  __/  / /_/ /___/ /
#  / .___/_/ /_/\__, /_/_/\____/_/ /_/ /_/\___/   \____//____/
# /_/          /____/

# SEOS-s, or the 'Still Enough Operating System for servers'

# * This script further remove packages installed on a fresh Fedora Server 34 minimal installation.
# * It may be suitable for a virtual machine or a virtualization host.
# * Packages have been sorted by themes, not alphabetical order.
# The name is a reference and hommage to the JEOS, the Just Enough OS mentioned in 'man virt-builder'

## CONTEXT
## Installed packages on Fedora Server vanilla : 614
## As provided by `dnf list --installed | wc -l´
## That is a lot of packages to track, and to keep updated.
## After the script has been run, the number should be closer to 300.

## IDEAS
# * Add link to support developers.
# * Breaks down the script to multiple sub-components
# * Breaks down the script based on themes
# * Create a script to do it in reverse (reinstall components)

## NOTES When quoted, the package or software definition has been fetched from the man page. When quoted and if a URL is available, the definition has been fetched from the website.

## We begin by uninstalling unused 'dnf groups'.
# 'groups' are packages that are bundled together to offer a generic functionality.
# The "Hardware Support" group further enhances support for hardware devices, especially for wireless cards.
# The "Headless Management" group provides cockpit, a solution to manage a server using a web browser.
dnf groupremove -y "Hardware Support"
dnf groupremove -y "Headless Management"

## NETWORK-RELATED

## ModemManager - mobile broadband modem management daemon
# ModemManager.x86_64
# ModemManager-glib.x86_64

## NetworkManager - network management daemon
## website : https://wiki.gnome.org/Projects/NetworkManager
# NetworkManager.x86_64
# NetworkManager-bluetooth.x86_64
# NetworkManager-libnm.x86_64
# NetworkManager-team.x86_64
# NetworkManager-wifi.x86_64
# NetworkManager-wwan.x86_64

## avahi-libs - Avahi is a system which facilitates service discovery on a local network
# avahi-libs.x86_64
## Depends on sssd (Open Source Client for Enterprise Identity Management) and samba
dnf remove -y avahi-libs

## bind - bind is a DNS system.
## website : https://www.isc.org/bind/
# bind-libs.x86_64
# bind-license.noarch
# bind-utils.x86_64

## chrony - "chrony is a versatile implementation of the Network Time Protocol (NTP)"
## website : https://chrony.tuxfamily.org/
# chrony.x86_64

## dhcp-client - the dhcp-client package provides the ISC DHCP client daemon and dhclient-script
## website : https://www.isc.org/dhcp/
# dhcp-client.x86_64
# dhcp-common.noarch

## dnmasq : "Dnsmasq provides network infrastructure for small networks, such as DNS and DHCP"
## website : https://thekelleys.org.uk/dnsmasq/doc.html
# dnsmasq.x86_64

## ethtool - tool to query or control network driver and hardware settings
## website : https://linux.die.net/man/8/ethtool
# ethtool.x86_64
dnf remove -y ethtool

## firewalld : "Firewalld provides a dynamically managed firewall with support for network/firewall zones that define the trust level of network connections or interfaces."
## website : https://firewalld.org/
# firewalld.noarch
# firewalld-filesystem.noarch


## DESKTOP-RELATED

## PackageKit  - PackageKit is a system designed to make installing and updating software on your computer easier.
## website : https://www.freedesktop.org/software/PackageKit/
# PackageKit.x86_64
# PackageKit-glib.x86_64
dnf remove -y PackageKit

## desktop-file-utils contains a few command line utilities for working with desktop entries
## website : https://www.freedesktop.org/wiki/Software/desktop-file-utils/
# desktop-file-utils.x86_64

## LOG-RELATED

## abrt - Manage problems handled by ABRT
## website : https://abrt.readthedocs.io/en/latest/howitworks.html
# abrt.x86_64
# abrt-addon-ccpp.x86_64
# abrt-addon-kerneloops.x86_64
# abrt-addon-pstoreoops.x86_64
# abrt-addon-vmcore.x86_64
# abrt-addon-xorg.x86_64
# abrt-cli.x86_64
# abrt-dbus.x86_64
# abrt-libs.x86_64
# abrt-plugin-bodhi.x86_64
# abrt-retrace-client.x86_64
# abrt-tui.x86_64
dnf remove -y abrt

## audit - allows to control the kernel audit system through the auditctl command
# audit.x86_64
# audit-libs.x86_64


## SECURITY-RELATED ##

## acl — Access Control Lists
## website : https://en.wikipedia.org/wiki/Access-control_list
# acl.x86_64

## cracklib : cracklib is a library for checking whether password is easily crackable or not
## sudo package depends on it
## website : https://github.com/cracklib/cracklib
# cracklib.x86_64
# cracklib-dicts.x86_64

## crypto-policies - Cryptographic policy management
## website : https://github.com/linux-system-roles/crypto_policies/
# crypto-policies.noarch
# crypto-policies-scripts.noarch

## cryptsetup - cryptsetup manages plain dm-crypt and LUKS encrypted volumes
# cryptsetup.x86_64
# cryptsetup-libs.x86_64
dnf remove -y cryptsetup

## cyrus
## website : https://www.cyrusimap.org/sasl/
## sudo depends on cyrus
# cyrus-sasl-gssapi.x86_64
# cyrus-sasl-lib.x86_64
# cyrus-sasl-plain.x86_64


## AUTHENTICATION ##

## adcli - Tool for performing actions on an Active Directory domain
# adcli.x86_64
dnf remove -y adcli

## authselect - select system identity and authentication sources.
# authselect.x86_64
# authselect-libs.x86_64


## SOUND ##

## API for sound cards
# alsa-lib.x86_64
# alsa-sof-firmware.noarch
## Can't be removed : depends on spice-vdagent


## COMMANDS AND SYSTEM-RELATED ##

## alternatives - maintain symbolic links determining default commands
# alternatives.x86_64

## at, batch, atq, atrm - queue, examine, or delete jobs for later execution
# at.x86_64

## augeas library. As described in their website, http://augeas.net/, "augeas is a # configuration editing tool. It parses configuration files in their native formats and # transforms them into a tree. Configuration changes are made by manipulating this tree and # saving it back into native config files."
# augeas-libs.x86_64

## basesystem - the basesystem package defines the components of a basic Fedora system, such as the package installation during bootstrapping."
# basesystem.noarch

## bash - the GNU Bourne-Again SHell (BASH)
# bash.x86_64
# bash-completion.noarch

## bc - An arbitrary precision calculator language
# bc.x86_64

## boost-regex - library that provides regular expression support for C++
# boost-regex.x86_64

## c-ares is a C library that performs DNS requests and name resolves asynchronously
# c-ares.x86_64

## ca-certificates
# ca-certificates.noarch

## coreutils - set of core utilities
# coreutils.x86_64
# coreutils-common.x86_64

## d-bus - "D-Bus is a message bus system, a simple way for applications to talk to one another"
## website : https://www.freedesktop.org/wiki/Software/dbus/
## systemd depends on dbus
# dbus.x86_64
# dbus-broker.x86_64
# dbus-common.noarch
# dbus-libs.x86_64
# dbus-tools.x86_64

## crontabs - configuration and scripts for running periodical jobs
# crontabs.noarch

## ctags - find objects in source files
## website : http://ctags.sourceforge.net/whatis.html
# ctags.x86_64
dnf remove -y ctags

## curl - curl is used in command lines or scripts to transfer data
## website : https://curl.se/download.html
## depends on grub2-pc
# curl.x86_64

## diffutils - GNU Diffutils is a package of several programs related to finding differences between files.
## website : https://www.gnu.org/software/diffutils/
# diffutils.x86_64
# policycoreutils depends on diffutils

## dmidecode - the dmidecode software fetches informations about your system's hardware from the system BIOS
## website : http://www.nongnu.org/dmidecode/
# dmidecode.x86_64

## ed - ed is a line line-oriented text editor
# info depends on ed.
# ed.x86_64

## elfutils : "elfutils is a collection of utilities and libraries to read, create and modify ELF binary files, find and handle DWARF debug data, symbols, thread state and stacktraces for processes and core files on GNU/Linux."
## website : https://sourceware.org/elfutils/
## kernel-core, systemd and systemd-udev depend on elfutils
# elfutils.x86_64
# elfutils-debuginfod-client.x86_64
# elfutils-default-yama-scope.noarch
# elfutils-libelf.x86_64
# elfutils-libs.x86_64

## expat - expat is an XML parser library
## systemd depends on expat
# expat.x86_64

## ######## ##
## ARCHIVES ##
## ######## ##

##  bzip2, bunzip2 - a block-sorting file compressor, v1.0.8
# bzip2.x86_64
# bzip2-libs.x86_64

## cpio : "GNU cpio copies files into or out of a cpio or tar archive, The archive can be another file on the disk, a magnetic tape, or a pipe."
## website : http://www.gnu.org/software/cpio/manual/cpio.html
# cpio.x86_64

## ######## ##
## HARDWARE ##
## ######## ##

## Firmware
# atmel-firmware.noarch
dnf remove -y atmel-firmware

## b43-fwcutter - utility for extracting Broadcom 43xx firmware
# b43-fwcutter.x86_64
dnf remove -y b43-fwcutter

## b43 - Open FirmWare for Broadcom 43xx series WLAN chip
# b43-openfwwf.noarch
dnf remove -y b43-openfwwf

## ######## ##
## FILE-SYSTEMS AND BLOCK DEVICES ##
## ######## ##

## attr - extended attributes on XFS filesystem objects
# attr.x86_64
## Useless for ext4
dnf remove -y attr

## btrfs - a toolbox to manage btrfs filesystems
# btrfs-progs.x86_64
dnf remove -y btrfs-progs

## cifs - tool to mount smb/cifs shares on Linux
# cifs-utils.x86_64
dnf remove -y cifs-utils

## compsize - compsize takes a list of files (given as arguments) on a btrfs filesystem and # measures used compression types and effective compression ratio
# compsize.x86_64
## Useless on ext4 systems
dnf remove -y compsize

## device-mapper : "The device mapper is provided by the Linux kernel to map physical block devices onto virtual block devices"
## grub2-tools-minimal depends on device-mapper
# device-mapper.x86_64
# device-mapper-libs.x86_64

## unix2dos - "Convert text files with DOS or Mac line breaks to Unix line breaks and vice versa."
## website : https://waterlan.home.xs4all.nl/dos2unix.html
# dos2unix.x86_64
dnf remove -y dos2unix

## dosfstools - "dosfstools consists of the programs mkfs.fat, fsck.fat and fatlabel to create, check and label file systems of the FAT family."
## website : https://github.com/dosfstools/dosfstools
# dosfstools.x86_64
dnf remove -y dosfstools

## e2fsprogs - e2fsprogs is a set of utilities to interact with ext2, ext3 and ext4 file systems
## website : http://e2fsprogs.sourceforge.net/
# e2fsprogs.x86_64
# e2fsprogs-libs.x86_64
dnf remove -y e2fsprogs

## exfatprogrs - exFAT filesystem userspace utilities
# exfatprogs.x86_64
dnf remove -y exfatprogs

## file — software that determines file type
# file.x86_64
# file-libs.x86_64

## filesystem - filesystem provides the basic directory layout for a Linux system
# filesystem.x86_64

## emacs-filesystem - ???
## pinfo depends on emacs-filesystem
# emacs-filesystem.noarch

## ######## ##
## BLUETHOOTH ##
## ######## ##

## bluez - The official Linux Bluetooth protocol stack
## website : http://www.bluez.org/
# bluez.x86_64
# bluez-libs.x86_64
dnf remove -y bluez*

## ######## ##
## PRINTING ##
## ######## ##

## cups - the Common UNIX Printing System (CUPS)
## website : http://www.cups.org/
# cups-libs.x86_64
dnf remove -y cups-libs

## ######## ##
## FEDORA-RELATED
## ######## ##

## dnf - dnf is the new package manager for Fedora
## website : https://rpm-software-management.github.io/
# dnf.noarch
# dnf-data.noarch
# dnf-plugins-core.noarch

## deltarpm : rpm package manager
## website : https://rpm.org/
# deltarpm.x86_64

## dracut - dracut is a set of tools to automate the Linux boot process
## website : https://dracut.wiki.kernel.org/index.php/Main_Page
# dracut.x86_64
# dracut-config-rescue.x86_64
# dracut-network.x86_64

## fedora-* - fedora signing gpg-key and packages linked to fedora repositories
# fedora-gpg-keys.noarch
# fedora-release-common.noarch
# fedora-release-identity-server.noarch
# fedora-release-server.noarch
# fedora-repos.noarch
# fedora-repos-modular.noarch


## ######## ##
## FONTS
## ######## ##

## dejavu-sans-fonts - package for dejavu font
# dejavu-sans-fonts.noarch
# dejavu-sans-mono-fonts.noarch

## fonts-filesystem - provides directories used by font packages
# fonts-filesystem.noarch

## findutils - "The GNU Find Utilities are the basic directory searching utilities of the GNU operating system".
## website : https://www.gnu.org/software/findutils/
## dracut depends on it
# findutils.x86_64



## fpaste - fpaste a cli frontend for the fpaste.org pastebin
# fpaste.noarch
dnf remove -y fpaste

## fprintd - Fingerprint management daemon, and test applications
# fprintd.x86_64
# fprintd-pam.x86_64
dnf remove -y fprintd

## fstrm - "This is fstrm, a C implementation of the Frame Streams data transport protocol."
## website : http://farsightsec.github.io/fstrm/
# fstrm.x86_64

## fuse-libs - "Fuselibs is the Uno-libraries that provide the UI framework used in Fuse apps."
## website : https://github.com/fuse-open/fuselibs
## grubs2-tools-minimal depends on fuse-libs
# fuse-libs.x86_64

## awk - awk search files for lines that contain certain patterns.
## website : https://www.gnu.org/software/gawk/
## sudo depends on gawk
# gawk.x86_64

## gc - the GNU compiler collection is a compiler
## website : http://gcc.gnu.org/
# gc.x86_64
dnf remove -y gc

## gdb-headless - gdb is a software debugger
# gdb-headless.x86_64
dnf remove -y gdb-headless

## gdbm-libs - GNU dbm (GDBD) is a library of database functions
## website : https://www.gnu.org.ua/software/gdbm/
## dnf depends of gdbm-libs
# gdbm-libs.x86_64

## gdk-pixbuf2 - "The Gdk Pixbuf package is a toolkit for image loading and pixel buffer manipulation."
## website (not official) : https://www.linuxfromscratch.org/blfs/view/svn/x/gdk-pixbuf.html
# gdk-pixbuf2.x86_64

## gettext - translate message
## grub2-pc depends on it
# gettext.x86_64
# gettext-libs.x86_64

## glib - "The GLib package contains low-level libraries useful for providing data structure handling for C, portability wrappers and interfaces for such runtime functionality as an event loop, threads, dynamic loading and an object system."
## website (not the official website) : https://www.linuxfromscratch.org/blfs/view/svn/general/glib2.html
## dnf, grub2-tools-minimal, sudo, systemd depend on glib
# glib-networking.x86_64
# glib2.x86_64
# glibc.x86_64
# glibc-common.x86_64
# glibc-doc.noarch
# glibc-langpack-en.x86_64

## gmp - gmp provides multiple precision arithmetic using the C library
## website : https://cran.r-project.org/web/packages/gmp/index.html
## grub2-pc, dnf, systemd depend on gmp
# gmp.x86_64

## gnupg2 - GnuPG is a free OpenPGP implementation
## website : https://gnupg.org/
## dnf, grub2-pc, systemd, dnf depend gnupg2
# gnupg2.x86_64

## gnutls - "GnuTLS is a secure communications library"
## website : https://gnutls.org/
# gnutls.x86_64

## gobject-introspection - "GObject introspection is a middleware layer between C libraries (using GObject) and language bindings"
## website : https://gi.readthedocs.io/en/latest/
## PackageKit depends on gobject-introspection
# gobject-introspection.x86_64
dnf remove -y gobject-introspection

## "GnuPG Made Easy (GPGME) is a library designed to make access to GnuPG easier for applications."
## website : https://www.gnupg.org/software/gpgme/index.html
## dnf depends on gpgme
# gpgme.x86_64

## grep - "grep is a command-line utility for searching plain-text data sets"
## website : https://en.wikipedia.org/wiki/Grep
# grep.x86_64

## groff - "groff - front-end for the groff document formatting system"
## website : (not official) https://linux.die.net/man/1/groff
## man-db depends on it
# groff-base.x86_64

## grub2 - bootloader
# grub2-common.noarch
# grub2-pc.x86_64
# grub2-pc-modules.noarch
# grub2-tools.x86_64
# grub2-tools-minimal.x86_64

## grubby - command line tool for configuring grub, lilo, and elilo
## website : (not official) https://linux.die.net/man/8/grubby
# grubby.x86_64

## gsettings-desktop-schemas - gsettings-desktop-schemas contains a collection of GSettings schemas for settings shared by various components of a desktop.
# gsettings-desktop-schemas.x86_64
dnf remove -y gsettings-desktop-schemas

## gssproxy - provides a daemon to manage access to GSSAPI (Generic Security Service Application Program Interface) credentials and security devices.
# gssproxy.x86_64

## guile - The GNU Project Extension Language. GNU  Guile  is  an  implementation of the Scheme programming language.
# guile.x86_64
dnf remove -y guile

## gziz - gunzip, zcat - compress or expand files
# gzip.x86_6

## hostname - show or set the system's host name
# hostname.x86_64

## hunspell - among other things, hunspell is a spell checker
# hunspell.x86_64
# hunspell-en.noarch
# hunspell-en-GB.noarch
# hunspell-en-US.noarch
# hunspell-filesystem.x86_64
dnf remove -y hunspell*

## hwdata - "hwdata contains various hardware identification and configuration data, such as the pci.ids and usb.ids databases".
## website : https://github.com/vcrhonek/hwdata
## pciutils, spice-vdagent and usbutils depends on it
# hwdata.noarch

## ima-evm-utils- "Integrity Measurement Architecture to know EXACTLY what has been run on your machine."
## website : https://sourceforge.net/projects/linux-ima/
## dnf depends on ima-evm-utils
# ima-evm-utils.x86_64

## info - read Info documents
## ed depends on info
# info.x86_64
dnf remove -y info

## initscripts - initscripts are scripts to bring up network interfaces and legacy utilities in Fedora, using the legacy System V system.
## audit depends on initscripts
# initscripts.x86_64
dnf remove -y initscripts

## ipcalc - ipcalc calculates IP information for a host or network.
# ipcalc.x86_64
## dhcp-client depends on ipcalc

## ipcalc - ipcalc calculates IP information for a host or network.
## dhcp-client depends on iproute
# iproute.x86_64

## ipset - "IP sets are a framework inside the Linux kernel, which can be administered by the ipset utility."
## website : https://ipset.netfilter.org/
## firewalld depends on ipset
# ipset.x86_64
# ipset-libs.x86_64

## iptables - "iptables is the userspace command line program used to configure the Linux 2.4.x and later packet filtering ruleset."
## website : https://www.netfilter.org/
## firewalld and iptstate depend on iptables
# iptables-compat.x86_64
# iptables-legacy.x86_64
# iptables-legacy-libs.x86_64
# iptables-libs.x86_64
# iptables-nft.x86_64
# iptables-utils.x86_64

## iptstate - "A top-like display of IP Tables state table entries"
# iptstate.x86_64
dnf remove -y ipstate

## iputils - iputils
## dhcp-client depends on iputils
# iputils.x86_64

## several firmware.
## Are they deleted when the dnf group "Hardware Support" is removed ?
# ipw2100-firmware.noarch
# ipw2200-firmware.noarch
dnf remove -y ipw2*

## irqbalance - distribute hardware interrupts across processors on a multiprocessor system
# numactl-libs depends on irqbalance
# irqbalance.x86_64

## iw - show / manipulate wireless devices and their configuration
# iw.x86_64
dnf remove -y iw

## iwd - Internet wireless daemon
# iwd.x86_64
dnf remove -y iwd

## Various wireless firmware.
## Are probably deleted when dnf group "Hardware Support" is removed
# iwl100-firmware.noarch
# iwl1000-firmware.noarch
# iwl105-firmware.noarch
# iwl135-firmware.noarch
# iwl2000-firmware.noarch
# iwl2030-firmware.noarch
# iwl3160-firmware.noarch
# iwl3945-firmware.noarch
# iwl4965-firmware.noarch
# iwl5000-firmware.noarch
# iwl5150-firmware.noarch
# iwl6000-firmware.noarch
# iwl6000g2a-firmware.noarch
# iwl6000g2b-firmware.noarch
# iwl6050-firmware.noarch
# iwl7260-firmware.noarch

## jansson - Jansson is a C library for dealing with JSON data
# jansson.x86_64
## firewalld, mtr, teamd, nftables depends on it

## json-c - "JSON-C implements a reference counting object model that allows you to easily construct JSON objects in C"
## website : http://json-c.github.io/json-c/
## systemd depends on json-c
# json-c.x86_64
# json-glib.x86_64

## jwhois - this is jwhois, an improved Whois client
## website : http://savannah.gnu.org/projects/jwhois/
# jwhois.x86_64
dnf remove -y jwhois

## kdb - tools for managing Linux console, i.e. loading console fonts and keyboard maps.
## website : http://kbd-project.org/
# kbd.x86_64
# kbd-misc.noarch

## kernel - the allmighty Linux kernel
## website : https://www.kernel.org/
# kernel.x86_64
# kernel-core.x86_64
# kernel-modules.x86_64

## kexec - boot a kernel from your currently running kernel
# kexec-tools.x86_64

## keyutils - in-kernel key management utilities, to accessing the kernel keyrings facility
## cifs-utils and nfs-utils depend on keyutils
# keyutils.x86_64
# keyutils-libs.x86_64

## kmod - kmod is a set of tools for managing Linux kernel modules
# kmod.x86_64
# kmod-libs.x86_64

## kpartx - kpartx Create device maps from partition tables
# kpartx.x86_64

## krb5 - kerberos library
## website : https://web.mit.edu/kerberos/krb5-1.16/doc/index.html
## sudo depends on krb5
# krb5-libs.x86_64

## langpacks-en - provides support for English
# langpacks-core-en.noarch
# langpacks-core-font-en.noarch
# langpacks-en.noarch

## less - less is a file pager, a tool that display a screen at a time
## website : https://packages.debian.org/stretch/less
# less.x86_64

## some libraries to X
# libX11.x86_64
# libX11-common.noarch
# libXau.x86_64
# libXext.x86_64
# libXfixes.x86_64
# libXinerama.x86_64
# libXrandr.x86_64
# libXrender.x86_64

## various libraries
# libacl.x86_64
# libappstream-glib.x86_64
# libarchive.x86_64
# libargon2.x86_64
# libassuan.x86_64
# libattr.x86_64
# libbabeltrace.x86_64
# libbasicobjects.x86_64
# libblkid.x86_64
# libbrotli.x86_64
# libcap.x86_64
# libcap-ng.x86_64
# libcbor.x86_64
# libcollection.x86_64
# libcom_err.x86_64
# libcomps.x86_64
# libcurl.x86_64
# libdaemon.x86_64
# libdb.x86_64
# libdhash.x86_64
# libdnf.x86_64
# libdrm.x86_64
# libeconf.x86_64
# libedit.x86_64
# libell.x86_64
# libertas-usb8388-firmware.noarch
# libestr.x86_64
# libev.x86_64
# libevent.x86_64
# libfastjson.x86_64
# libfdisk.x86_64
# libffi.x86_64
# libfido2.x86_64
# libfprint.x86_64
# libgcc.x86_64
# libgcrypt.x86_64
# libgomp.x86_64
# libgpg-error.x86_64
# libgudev.x86_64
# libgusb.x86_64
# libibverbs.x86_64
# libicu.x86_64
# libidn2.x86_64
# libini_config.x86_64
# libipa_hbac.x86_64
# libipt.x86_64
# libjpeg-turbo.x86_64
# libkcapi.x86_64
# libkcapi-hmaccalc.x86_64
# libksba.x86_64
# libldb.x86_64
# libmaxminddb.x86_64
# libmbim.x86_64
# libmbim-utils.x86_64
# libmetalink.x86_64
# libmnl.x86_64
# libmodulemd.x86_64
# libmount.x86_64
# libndp.x86_64
# libnetfilter_conntrack.x86_64
# libnfnetlink.x86_64
# libnfsidmap.x86_64
# libnftnl.x86_64
# libnghttp2.x86_64
# libnl3.x86_64
# libnl3-cli.x86_64
# libnsl2.x86_64
# libpasswdqc.x86_64
# libpath_utils.x86_64
# libpcap.x86_64
# libpciaccess.x86_64
# libpipeline.x86_64
# libpkgconf.x86_64
# libpng.x86_64
# libproxy.x86_64
# libpsl.x86_64
# libpwquality.x86_64
# libqmi.x86_64
# libqmi-utils.x86_64
# libqrtr-glib.x86_64
# libref_array.x86_64

## libraries associated to reporting
# librepo.x86_64
# libreport.x86_64
# libreport-cli.x86_64
# libreport-fedora.x86_64
# libreport-filesystem.noarch
# libreport-plugin-bugzilla.x86_64
# libreport-plugin-kerneloops.x86_64
# libreport-plugin-logger.x86_64
# libreport-plugin-systemd-journal.x86_64
# libreport-plugin-ureport.x86_64
# libreport-web.x86_64

## libseccomp - library associated to seccomp
# libseccomp.x86_64

## libselinux - library associated to libselinux
# libselinux.x86_64
# libselinux-utils.x86_64

## misc libraries - to be investigated
# libsemanage.x86_64
# libsepol.x86_64
# libsigsegv.x86_64
# libsmartcols.x86_64
# libsmbclient.x86_64
# libsolv.x86_64
# libsoup.x86_64
# libss.x86_64

## librairies used by ssh ?
# libssh.x86_64
# libssh-config.noarch

## librairies used by sssd ?
# libsss_autofs.x86_64
# libsss_certmap.x86_64
# libsss_idmap.x86_64
# libsss_nss_idmap.x86_64
# libsss_sudo.x86_64

## various libraries
# libstdc++.x86_64
# libstemmer.x86_64
# libtalloc.x86_64
# libtasn1.x86_64
# libtdb.x86_64
# libteam.x86_64
# libtevent.x86_64
# libtextstyle.x86_64
# libtirpc.x86_64
# libtool-ltdl.x86_64
# libunistring.x86_64
# liburing.x86_64
# libusbx.x86_64
# libuser.x86_64
# libutempter.x86_64
# libuuid.x86_64
# libuv.x86_64
# libverto.x86_64
# libverto-libev.x86_64
# libwbclient.x86_64
# libxcb.x86_64
# libxcrypt.x86_64
# libxcrypt-compat.x86_64
# libxkbcommon.x86_64
# libxml2.x86_64
# libyaml.x86_64
# libzstd.x86_64

## linux-firmware - Firmware files for Linux
# linux-firmware.noarch
# linux-firmware-whence.noarch

## lmdb - database linked to openLDAP ?
# lmdb-libs.x86_64

## logrotate - rotates, compresses, and mails system logs
## website : https://linux.die.net/man/8/logrotate
# logrotate.x86_64
dnf remove -y logrotate

## lsof - list open files
## website : https://en.wikipedia.org/wiki/Lsof
# lsof.x86_64

## lua-libs - "lua-libs is a collection of utilities, oop, linked list, memoization, memento, flyweight, string manipulation"
## website : (not official) http://lua-users.org/wiki/LibrariesAndBindings
# lua-libs.x86_64

## lz4-libs - LZ4 is lossless compression algorithm
## website : https://lz4.github.io/lz4/
## systemd depends on lz4-libs
# lz4-libs.x86_64

## lzo - lzo: real-time data compression library
# lzo.x86_64
dnf remove -y lzo

## mailcap - metamail capabilities file
## website : https://linux.die.net/man/4/mailcap
# mailcap.noarch
dnf remove -y mailcap

## man-pages - conventions for writing Linux man pages
# man-db.x86_64
# man-pages.noarch
dnf remove -y man-db

## mcelog - mcelog logs and accounts machine checks on modern x86 Linux systems.
## website : http://mcelog.org/
# mcelog.x86_64
dnf remove -y mcelog

## mdadm - manage software RAID
# mdadm.x86_64
dnf remove -y mdadm

## microcode_ctl - "microcode utility to flash Intel CPUs on boot"
## website : (not official) https://linux.die.net/man/8/microcode_ctl
# microcode_ctl.x86_64

## mlocate - a tool to find files in the filesystem based on their name
# mlocate.x86_64
dnf remove -y mlocate

## mozjs78 - mozjs78 is a standalone Mozilla JavaScript engine
# mozjs78.x86_64
dnf remove -y mozjs78

## mpfr - MPFR is based on the GMP multiple-precision library
## website : https://www.mpfr.org/
# mpfr.x86_64

## mtr - mtr is a real-time network diagnostic tool
# mtr.x86_64
## website : https://www.redhat.com/sysadmin/linux-mtr-command
dnf remove -y mtr

## nano - nano is a text editor
# nano.x86_64
# nano-default-editor.noarch

## ncurses - "ncurses is a programming library providing an application programming interface that allows the programmer to write text-based user interfaces in a terminal-independent manner." https://invisible-island.net/ncurses/announce.html
# ncurses.x86_64
# ncurses-base.noarch
# ncurses-libs.x86_64

## net-tools - Linux networking base tools
# net-tools.x86_64

## nettle - Nettle is a cryptographic library that is designed to fit easily in more or less anycontext: In crypto toolkits for object-oriented languages (C++, Python, Pike, ...), inapplications like LSH or GNUPG, or even in kernel space.
## website : https://www.lysator.liu.se/~nisse/nettle/
# nettle.x86_64

## nfs-utils, the Linux NFS userland utility package.
# nfs-utils.x86_64
dnf remove -y nfs-utils

## nftables - "nftables is the successor of iptables, it allows for much more flexible, scalable and performance packet classification".
## website : https://www.nftables.org/
# nftables.x86_64

## nmap-ncat - "ncat is a feature-packed networking utility which reads and writes data across networks from the command line"
## website : https://nmap.org/ncat/
# nmap-ncat.x86_64
dnf remove -y nmap-ncat

## nPth is a non-preemptive threads implementation
# npth.x86_64

## nspr - Netscape Portable Runtime. NSPR provides platform independence for non-GUI operating system facilities.
# nspr.x86_64
dnf remove -y nspr

## nss - Name Service Switch configuration file
# nss.x86_64
# nss-softokn.x86_64
# nss-softokn-freebl.x86_64
# nss-sysinit.x86_64
# nss-util.x86_64

## ntfs-3g - Third Generation Read/Write NTFS Driver
# ntfs-3g.x86_64
dnf remove -y ntfs-3g

## ntfsprogs - tools for doing neat things with NTFS
# ntfsprogs.x86_64

## numactl-libs - The libnuma library offers a simple programming interface to the NUMA (Non Uniform Memory Access) policy supported by the Linux kernel
## website : https://linux.die.net/man/3/numa
# numactl-libs.x86_64

## openldap - the openLDAP directory
## sudo depends on openldap
# openldap.x86_64

## opensc - smart card utilities
# opensc.x86_64
dnf remove -y opensc

## openssh
# openssh.x86_64
# openssh-clients.x86_64
# openssh-server.x86_64

## openssl - a general purpose cryptography library with TLS implementation
# openssl-libs.x86_64

## os-prober - discover bootable partitions on the local system. See https://www.linux.org/docs/man1/os-prober.html
## grub2-pc depends on os-proper
# os-prober.x86_64

## p11-kit - "Provides a way to load and enumerate PKCS#11 modules"
## website : https://p11-glue.github.io/p11-glue/p11-kit.html
## systemd depends on p11-kit
# p11-kit.x86_64
# p11-kit-trust.x86_64

## pam - Pluggable Authentication Modules (PAM) for Linux
## website : http://www.linux-pam.org/
# pam.x86_64
# pam_passwdqc.x86_64

## parted - parted manipulates partitions
## website : http://www.gnu.org/software/parted/
# parted.x86_64
dnf remove -y parted

## passwd - update user's authentication tokens
# passwd.x86_64
# passwdqc.x86_64
# passwdqc-utils.x86_64

## pcituils - "The PCI Utilities package contains a library for portable access to PCI bus configuration registers and several utilities based on this library."
## website : https://github.com/pciutils/pciutils
# pciutils.x86_64
# pciutils-libs.x86_64

## pcre - pcre (Perl Compatible Regular Expressions) provides regular expressions for Perl
## website : http://www.pcre.org/
# pcre.x86_64
# pcre2.x86_64
# pcre2-syntax.noarch

## pcsc - pcsc is "a middleware to access a smart card using SCard API (PC/SC)".
## website : https://pcsclite.apdu.fr/
## opensc depends on pcsc
# pcsc-lite.x86_64
# pcsc-lite-ccid.x86_64
# pcsc-lite-libs.x86_64

## pinfo - pinfo is used to view info files
## info depends on pinfo
# pinfo.x86_64

## pixman - "Pixman is a low-level software library for pixel manipulation"
## website : http://pixman.org/
## nss depends on pixman
# pixman.x86_64

## pkgconf - "pkgconf is a program which helps to configure compiler and linker flags for development libraries. It is similar to pkg-config from freedesktop.org."
## website : https://github.com/pkgconf/pkgconf
# pkgconf.x86_64
# pkgconf-m4.noarch
# pkgconf-pkg-config.x86_64

## plymouth - "Plymouth is an application that runs very early in the boot process (even before the root filesystem is mounted!) that provides a graphical boot animation while the boot process happens in the background."
## website : https://www.freedesktop.org/wiki/Software/Plymouth/
# plymouth.x86_64
# plymouth-core-libs.x86_64
# plymouth-scripts.x86_64

## policycoreutils - SELinux policy core utilities
## website : http://www.selinuxproject.org/page/Main_Page
# policycoreutils.x86_64

## polkit - "polkit is a toolkit for defining and handling authorizations.  It is used for allowing unprivileged processes to speak to privileged processes."
## website : https://gitlab.freedesktop.org/polkit/polkit/
## realmd and opensc depend on polkit
# polkit.x86_64
# polkit-libs.x86_64
# polkit-pkla-compat.x86_64
dnf remove -y polkit

## popt - "The library popt parses options in command lines in Linux and other Unix-like systems."
## website - https://github.com/devzero2000/POPT
# popt.x86_64

## procps - "Command line and full screen utilities for browsing procfs, a "pseudo" file system dynamically generated by the kernel to provide information about the status of entries in its process table."
# procps-ng.x86_64

## protobuf - Protocol Buffers implementation in C
## bind-utils depends on protobuf-c
# protobuf-c.x86_64

## psacct - psacct is responsible for starting and stopping processes at boot time and during system shutdown
# psacct.x86_64

## psmisc - "A package of small utilities that use the proc file-system."
## website : https://gitlab.com/psmisc/psmisc
# psmisc.x86_64

## publicsuffix - "Cross-vendor public domain suffix database in DAFSA form"
## website : https://publicsuffix.org/learn/
# publicsuffix-list-dafsa.noarch

## python-related - to-do
# python-pip-wheel.noarch
# python-setuptools-wheel.noarch
# python-unversioned-command.noarch

## python3-related - to-do
# python3.x86_64
# python3-abrt.x86_64
# python3-abrt-addon.noarch
# python3-argcomplete.noarch
# python3-augeas.noarch
# python3-dateutil.noarch
# python3-dbus.x86_64
# python3-decorator.noarch
# python3-distro.noarch
# python3-dnf.noarch
# python3-dnf-plugins-core.noarch
# python3-firewall.noarch
# python3-gobject-base.x86_64
# python3-gpg.x86_64
# python3-hawkey.x86_64
# python3-libcomps.x86_64
# python3-libdnf.x86_64
# python3-libreport.x86_64
# python3-libs.x86_64
# python3-libselinux.x86_64
# python3-libxml2.x86_64
# python3-nftables.x86_64
# python3-pexpect.noarch
# python3-pip.noarch
# python3-ptyprocess.noarch
# python3-rpm.x86_64
# python3-setuptools.noarch
# python3-six.noarch
# python3-slip.noarch
# python3-slip-dbus.noarch
# python3-systemd.x86_64

## qemu-guest-agent - "The QEMU Guest Agent is a daemon intended to be run within virtual machines"
## website : https://qemu.readthedocs.io/en/latest/interop/qemu-ga-ref.html
# qemu-guest-agent.x86_64

## quota - display disk usage and limits
## website : (not official) https://linux.die.net/man/1/quota
## nfs-utils depends on quota
# quota.x86_64

## quota-nls - "Gettext catalogs for disk quota tools"
## website : https://pkgs.org/download/quota-nls
# quota-nls.noarch

## readline - allows to edit command lines as they are typed in
## website : https://tiswww.case.edu/php/chet/readline/rltop.html
## systemd depends on readline
# readline.x86_64

## realmd - "realmd is an on demand system DBus service, which allows callers to configure network authentication and domain membership in a standard way"
## website - https://freedesktop.org/software/realmd/
# realmd.x86_64

## rootfiles - the root file system
# rootfiles.noarch

## rpcbind - universal addresses to RPC program number mapper
## nfs-utils depends on rcbind
## website - (not official) https://linux.die.net/man/8/rpcbind
# rpcbind.x86_64


## rpm - "The RPM Package Manager (RPM) is a powerful package management system"
## website : https://rpm.org/
# rpm.x86_64
# rpm-build-libs.x86_64
# rpm-libs.x86_64
# rpm-plugin-selinux.x86_64
# rpm-sign-libs.x86_64
# rpmfusion-free-release.noarch

## rsync - a fast, versatile, remote (and local) file-copying tool
# rsync.x86_64
dnf remove -y rsync

## rsyslogd - reliable and extended syslogd
# rsyslog.x86_64

## samba-client - "Samba is the standard Windows interoperability suite of programs for Linux and Unix."
## website : https://www.samba.org/
# samba-client-libs.x86_64
# samba-common.noarch
# samba-common-libs.x86_64
dnf remove -y samba-client

## satyr - "satyr is a command line tool that creates anonymous reports of software problems that are suitable for automated processing."
## website : https://github.com/abrt/satyr
# satyr.x86_64

## sed - sed (stream editor) is a non-interactive command-line text editor.
## website : https://www.gnu.org/software/sed/
## grub2-pc depends on sed
# sed.x86_64

## selinux-policy - "The SELinux Policy is the set of rules that guide the SELinux security engine."
## website : https://web.mit.edu/rhel-doc/5/RHEL-5-manual/Deployment_Guide-en-US/rhlcommon-chapter-0001.html
# selinux-policy.noarch
# selinux-policy-targeted.noarch

## ???
# setup.noarch

## shadow-utils - "Utilities for managing accounts and shadow password files"
## website : https://yum-info.contradodigital.com/view-package/installed/shadow-utils/
# shadow-utils.x86_64

## shared-mime-info - MIME database to represent types of files.
## website - https://freedesktop.org/wiki/Specifications/shared-mime-info-spec/
## PackageKit depends on shared-mime-info
# shared-mime-info.x86_64
dnf remove -y shared-mime-info

## smartmontools - "The smartmontools package contains two utility programs (smartctl and smartd) to control and monitor storage systems using the Self-Monitoring, Analysis and Reporting Technology System (SMART)" - https://www.smartmontools.org/
# smartmontools.x86_64

## snappy - the snappy package manager ?
# snappy.x86_64

## sos - tool that collects configuration details, system information and diagnostic information about the system.
## abrt depends on sos
# sos.noarch

## source-highlight - Given a source file, GNU Source-highlight produces a document with syntax highlighting.
## website : https://www.gnu.org/software/src-highlite/
# source-highlight.x86_64

## spice-vdagent
## website - https://www.spice-space.org/download.html
# spice-vdagent.x86_64

## sqlite-libs - C library that implements a SQL database engine
## website - https://sqlite.org/index.html
## dnf depends on sqlite-libs
# sqlite-libs.x86_64

## sssd - the System Security Services Daemon (SSSD) allows Linux machines to enroll in AD, FreeIPA or LDAP
# sssd.x86_64
# sssd-ad.x86_64
# sssd-client.x86_64
# sssd-common.x86_64
# sssd-common-pac.x86_64
# sssd-ipa.x86_64
# sssd-kcm.x86_64
# sssd-krb5.x86_64
# sssd-krb5-common.x86_64
# sssd-ldap.x86_64
# sssd-nfs-idmap.x86_64
# sssd-proxy.x86_64
dnf remove -y sssd*

## sudo, sudoedit — sudo allows to execute a command as another user
# sudo.x86_64

## symlinks - symbolic link maintenance utility
# symlinks.x86_64

## systemd - "systemd is a suite of basic building blocks for a Linux system".
## website : https://systemd.io/
# systemd.x86_64
# systemd-libs.x86_64
# systemd-networkd.x86_64
# systemd-oomd-defaults.x86_64
# systemd-pam.x86_64
# systemd-rpm-macros.noarch
# systemd-udev.x86_64

## tar — format of tape archive files
# tar.x86_64
dnf remove -y tar

## tcl - Facilities for package loading and version control
## website : https://www.astro.princeton.edu/~rhl/Tcl-Tk_docs/tcl/package.n.html
# tcl.x86_64
dnf remove -y tcl

## tcpdump - dump traffic on a network
# tcpdump.x86_64
dnf remove -y tcpdump

## teamd - networking teaming or bonding
## website : (unofficial) https://fedoraproject.org/wiki/Features/Team
# teamd.x86_64

## time - "time a simple command or give resource usage"
# time.x86_64
dnf remove -y time

## tpm2-tss - "Trusted Computing Group's (TCG) TPM2 Software Stack (TSS)."
## website : https://tpm2-tss.readthedocs.io/en/latest/index.html
# tpm2-tss.x86_64

## traceroute - computer network diagnostic tool
# traceroute.x86_64
dnf remove -y traceroute

## tree - list contents of directories in a tree-like format.
# tree.x86_64

## tzdata - control and set timezones
# tzdata.noarch

## unzip - list, test and extract compressed files in a ZIP archive
# unzip.x86_64
dnf remove -y unzip

## usb_modeswitch - control the mode of 'multi-state' USB devices
# usb_modeswitch.x86_64
# usb_modeswitch-data.noarch
dnf remove -y usb_modeswitch

## usbutils - collection of usb tools to query what type of usb devices are connected to the system
# usbutils.x86_64
dnf remove -y usbutils

## util-linux - "util-linux is a random collection of Linux utilities"
## website : https://github.com/karelzak/util-linux
# util-linux.x86_64
# util-linux-user.x86_64

## vim-minimal - the vi editor
## website : https://www.vim.org/
# vim-minimal.x86_64

## wget - non-interactive network downloader
## website : http://www.gnu.org/software/wget/
# wget.x86_64
dnf remove -y wget

## which - shows the full path of (shell) commands.
## grub2-pc depends on which
# which.x86_64

## wireless-regdb - wireless regulatory database for Linux
# wireless-regdb.noarch
dnf remove -y wireless-regdb

## ???
# words.noarch

## xdg-utils - xdg-utils is a set of tools to integrate applications in a desktop
## website : https://freedesktop.org/wiki/Software/xdg-utils/
# xdg-utils.noarch
dnf remove -y xdg-utils

## xkeyboard-config
## website : https://github.com/freedesktop/xkeyboard-config
# xkeyboard-config.noarch

## xmlrpc-c - "XML-RPC is a quick-and-easy way to make procedure calls over the Internet."
## website : http://xmlrpc-c.sourceforge.net/
# xmlrpc-c.x86_64
# xmlrpc-c-client.x86_64

## xxhash-libs - "xxHash is an extremely fast non-cryptographic hash algorithm"
## website : https://cyan4973.github.io/xxHash/
# xxhash-libs.x86_64

## xz - "Compress or decompress .xz and .lzma files"
# xz.x86_64
# xz-libs.x86_64

## yum - yellowdog updater modified (yum) "is an automatic updater and package installer/remover for rpm systems"
## website : http://yum.baseurl.org/
# yum.noarch

## zchunk - compressed file format that provides easy deltas
# zchunk-libs.x86_64

## just another firware
# zd1211-firmware.noarch
dnf remove -y zd1211

## zip - package and compress files
# zip.x86_64
dnf remove -y zip

## zlib
## website : https://www.zlib.net/
# zlib.x86_64

## zram - "zram-generator - Systemd unit generator for zram swap devices"
# zram-generator.x86_64
# zram-generator-defaults.noarch