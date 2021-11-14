# Phyllome OS

> Virtualization for the rest of us

*Phyllome OS is a [Fedora Remix](https://fedoraproject.org/wiki/Remix) based on [Fedora Server 35](https://getfedora.org/en/server/) designed to leverage hardware-assisted virtualization and VirtIO-based paravirtualization to make it easier to run modern UEFI-compatible guest operating systems locally.*

> This is the **alpha version** of Phyllome OS. Expect bugs and disappointment.

> External contributions for Phyllome OS are welcome. Have a look [here](https://kanboard.phyllo.me/b/CH7qd98J2v7egmodk/development) for some ideas on what to do next, or feel free to create an issue and suggest an idea you wish to work on. 

> The Phyllome OS Project is **looking** for **core contributors**, willing to contribute regularly on the project. If you are interested about making cutting-edge open-source virtualization more accessible, please send an email to contact@phyllo.me.

## What

This repository contains the basic building blocks required for deploying [Phyllome OS](https://phyllo.me/) in a virtual machine, using kickstart files. 

Kickstart files are used to automate the installation and configuration of RPM-based operating systems.

> If you would like to install Phyllome OS on your computer, please follow [this guide](https://wiki.phyllo.me/deploy/install) instead.

### Structure of the repository

* `blocks` : this directory contains the basic building blocks for assembling Phyllome OS Desktop and Phyllome OS Server.
    * This is where most of the development happens.
* `blocks-live` : this directory contains the basic building blocks for creating a live medium for Phyllome OS.
    * The code in this directory usually lags behind what is found in the `blocks` directory. 
    * Ideally, the `blocks` and `blocks-live` repository would be merged, and the number of blocks reduced, to avoid code duplication.  
* `leaves` : this directory contains the end product in the form of stand-alone and ready-to-use kickstart files.
    * For instance, the Phyllome OS Desktop version optimized for Intel(tm) CPUs and Intel(tm) graphics cards, refered internally as `flat-dhi`, is stored there (*d* stands for desktop, *h* for hypervisor and *i* for intel).
* `post` : this directory contains scripts that are meant to be run after a successful installation, after Phyllome OS has started
    * Ideally, these code snippets will be merged with existing building blocks, or summoned as a systemd unit.

## How to hack Phyllome OS

> Only Linux-based development is possible at the moment, sorry. Support for macOS and Windows-based development will follow.

As of now, hacking kickstart files is the main way to develop Phyllome OS. 

Have a look [here](https://docs.fedoraproject.org/en-US/fedora/rawhide/install-guide/appendixes/Kickstart_Syntax_Reference/) to learn the kickstart syntax.

### Requirements

* A Linux distribution, with a recent Linux Kernel (> 5.X)
* A x86_64 platform with hardware-assisted virtualization [enabled](https://wiki.phyllo.me/deploy/prepare)
* Nested-virtualization enabled
* `virt-install` and `virt-manager`, as well as `libvirt` and `qemu-kvm` up and running

**Enable** nested-virtualization on **AMD-based systems**, then reboot:

```
sudo echo "options kvm_amd nested=1" >> /etc/modprobe.d/kvm.conf
```

**Enable** nested-virtualization on **Intel-based systems**, then reboot:

```
sudo echo "options kvm_intel nested=1" >> /etc/modprobe.d/kvm.conf`
```

**Install the prerequisites on Fedora 35**

```
sudo dnf install -y qemu-kvm libvirt libvirt-daemon-config-network libvirt-daemon-kvm virt-install virt-top virt-manager libguestfs-tools python3-libguestfs guestfs-tools pykickstart
```

**Install the prerequisites on Ubuntu 20.4 or Debian 11**

```To be done```

### Hack around

Clone this repository:

```
git clone https://github.com/PhyllomeOS/PhyllomeOS.git
```

Modify some files, typically inside the `blocks` directory.

When you are done, move to the `flat` directory:

```
cd ./PhyllomeOS/flat/
```

Then, merge the kickstart basic building blocks into a single file, a process called flattening.

```
ksflatten -c ../blocks/dhi.cfg -o flat-dhi.cfg
```
If any error is detected, go back and fix them.

### Fire it up!

For testing purposes, Phyllome OS can be deployed inside a virtual machine, as a guest hypervisor.

The following command will automatically deploy the alpha version of Phyllome OS, tuned for Intel CPUs and Intel graphics cards.

It uses a Q35 virtual motherboard, a UEFI-based firmware, virtio-devices accross the board, 2 vCPUs, 4 GB of RAM and a disk of 5 GB.

> Adjust it according to your need. 

When ready, copy and paste it to your terminal.

```
virt-install \
    --connect qemu:///system \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name phyllome-alpha \
    --boot uefi \
    --cpu host-model,topology.sockets=1,topology.cores=2,topology.threads=1 \
    --vcpus 2 \
    --memory 4096 \
    --video virtio \
    --channel spicevmc \
    --autoconsole none \
    --sound none \
    --controller type=virtio-serial \
    --controller type=usb,model=none \
    --controller type=scsi,model=virtio-scsi \
    --network network=default,model=virtio \
    --input type=keyboard,bus=virtio \
    --input type=tablet,bus=virtio \
    --rng /dev/urandom,model=virtio \
    --disk path=/var/lib/libvirt/images/flat-dhi.img,format=raw,bus=virtio,cache=writeback,size=5 \
    --location=https://download.fedoraproject.org/pub/fedora/linux/releases/35/Everything/x86_64/os/ \
    --initrd-inject flat-dhi.cfg --extra-args "inst.ks=file:flat-dhi.cfg"
```
You should see the following message. 
```
Starting install...
Retrieving file vmlinuz...                                  |  10 MB  00:00     
Retrieving file initrd.img...                               |  79 MB  00:02     
Allocating 'virtinst-inlu7cmw-vmlinuz'                      |  10 MB  00:00     
Transferring virtinst-inlu7cmw-vmlinuz                      |  10 MB  00:00     
Allocating 'virtinst-2dd8ghse-initrd.img'                   |  79 MB  00:00     
Transferring virtinst-2dd8ghse-initrd.img                   |  79 MB  00:01     
Allocating 'flat-dhi.img'                                 | 5.0 GB  00:00     

Domain is still running. Installation may be in progress.
You can reconnect to the console to complete the installation process.
```
The installation process will be launched behind the scene. You can open `virt-manager` and connect to the virtual machine console to follow the process. Eventually, you will be greeted with this screen:

![greetings](./img/greetings.png)

After you are done setting your user account, `virt-manager` will automatically start:

![greetings](./img/desktop.png)

If the installation is a success and your feature is working as intended, you are welcome to create a pull request. Thank you!

## Phyllome OS 

Phyllome OS goal is to maximize ease-of-use and compatibility. As such, it intends to become the easiest way to virtualize modern operating systems locally, by integrating pertinent open-source software such as `libvirt`, `qemu-kvm` (and eventually `Cloud Hypervisor`), as well as `virt-manager`.

A user should not have to manage Phyllome OS: it should be able to pick its favorite operating system and Phyllome OS should run it, no question asked.

> Note : at the exception of open-source [Darwin derivatives](https://en.wikipedia.org/wiki/Darwin_(operating_system)#Derived_projects), Phyllome OS **strongly** discourage users from running proprietary, darwin-based derivatives on non-Apple hardware.

### The Phyllome OS Project

The Phyllome OS Project relies on multiple tools, including the following public-facing tools: 

* **Wiki**: Have a look at the [wiki repository](https://github.com/PhyllomeOS/wiki) for more information on how you can contribute to improve the documentation.
* **Issues tracker**: a public, read-only issue tracking is [available online](https://kanboard.phyllo.me/b/CH7qd98J2v7egmodk/development). For now one, GitHub issue tracking will be used to track development only issues.  
* **Code repository**: GitHub is used to host the code, with a mirror pointing to git.phyllo.me

## Licence

* [MIT](./LICENSE.md) for the most part, with some [GPL](./blocks-live/LICENSE.md) code.

## Acknowledgement

Thanks to the main contributors of the official Fedora kickstart files repository, and related tools:

> Adam Miller, Bastien Nocera, Bruno Wolff III, Bryan Kearney, Chitlesh Goorah, Christoph Wickert, 
Colin Walters, Fabian Affolter, Igor Pires Soares, Jens Petersen, Jeremy Katz, Jeroen van Meeuwen
Jesse Keating, Luya Tshimbalanga, Matthias Clasen, Pedro Silva, Rahul Sundaram, Sebastian Dziallas
Sebastian Vahl, wart. More information here : https://pagure.io/fedora-kickstarts
