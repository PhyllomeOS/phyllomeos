# Phyllome OS

> Virtualization for the rest of us

## What 

This repository contains the basic building blocks required for deploying [Phyllome OS](https://phyllo.me/) bare-metal or in a virtual machine, using kickstart files.

> Note: This is the **alpha version** of Phyllome OS. Expect bugs and disappointment

> Note: External contributions for Phyllome OS itself are **not** yet accepted. However, the Phyllome OS Project is looking for **core contributors**. If you are interested about making cutting-edge open-source virtualization more accessible, please send an email to contact@phyllo.me.

### Structure of the repository

* `leaves` : this directory contains the basic buildings blocks for assembling Phyllome OS versions
    * For instance, the Phyllome OS Desktop version optimized for Intel(tm) CPUs and Intel(tm) graphic cards, refered internally as `dhi`, can be found there (*d* for desktop; *h* for hypervisor; *i* for intel)
    * Eventually, there will be three generic editions : **server**; **desktop** and **live**, with their own platform-dependant optimizations 
* `flat` : this directory contains the end products in the form of stand-alone and ready-to-use kickstart files

## How to hack

Hacking kickstart files is the main way to assemble and configure Phyllome OS, which is RPM-based. Kickstart files are snippets of code which automate the installation of RPM-based Linux distributions.

### Requirements

* A x86_64 platform with hardware-assisted virtualization enabled
* A recent Linux Kernel (> 5.X)
* The `virt-install` and `virt-manager` tools
* `libvirt` and `qemu-kvm` up and running
* Nested-virtualization enabled 

### The prerequisites

**AMD-based systems only**, enable nested-virtualization, then reboot:

```
sudo echo "options kvm_amd nested=1" >> /etc/modprobe.d/kvm.conf
```

**Intel-based systems only**, enable nested-virtualization, then reboot:

```
sudo echo "options kvm_intel nested=1" >> /etc/modprobe.d/kvm.conf`
```

Install the prerequisites on Fedora 34

```
sudo dnf install -y qemu-kvm libvirt libvirt-daemon-config-network libvirt-daemon-kvm virt-install virt-top virt-manager libguestfs-tools python3-libguestfs guestfs-tools
```

Install the prerequisites on Ubuntu 20.4 or Debian 11

```To be done```

### Hack

From within your favorite terminal :

```
git clone https://github.com/PhyllomeOS/PhyllomeOS.git
```

Hack files inside the `leaves` directory.

When you are done, move to the `flat` directory :

```
cd ./PhyllomeOS/flat/
```

Then, merge the kickstart leaves into a single file, a process known as flattening. Here, we take the Phyllome OS Desktop edition optimized for Intel(tm) CPUs and Intel(tm) graphic cards, also known as `dhi`, as an example :

```
ksflatten -c ../leaves/dhi.cfg -o flat-dhi.cfg
```

## Fire it up!

For testing and development purposes, Phyllome OS can be deployed inside a virtual machine, as a guest hypervisor.

> Note: it may eventually switch to container-based development.

> Note: the following script relies on a network-accessible kickstart file tuned for Intel CPUs and GPUs.

This script will automatically deploy the alpha version of Phyllome OS, on a Q35 virtual motherboard, a UEFI-based firmware, virtio-devices accross the board, 2 vCPUs, 4 GB of RAM and a disk of 5 GB. 

Adjust it according to your need. When ready, copy and paste it to your terminal and fire it up!

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
The process will be launched behind the scene. You can open `virt-manager` and connect to the virtual machine to follow the process. Eventually, you will be greated with this screen:

![greetings](./img/greetings.png)

After you are done setting your user account, `virt-manager` will automatically start:

![greetings](./img/desktop.png)

## Phyllome OS 

Phyllome OS is a [Fedora Remix](https://fedoraproject.org/wiki/Remix) based on [Fedora Server 34](https://getfedora.org/en/server/) designed to leverage hardware-assisted virtualization and VirtIO-based paravirtualization to run modern UEFI-compatible guest operating systems locally.

The goal is to maximize ease-of-use and compatibility. As such, Phyllome OS intends to become the easiest way to virtualize modern operating systems, by integrating pertinent open-source software such as `libvirt`, `qemu-kvm` (and then the `Cloud Hypervisor`) and `virt-manager`.

A user should not have to manage Phyllome OS: it should be able to pick its favorite operating system and Phyllome OS should run it, no question asked.

Do you want to know more about Phyllome OS design and context ? If so, please have a look at [the white paper]().

> Note : at the exception of open-source [Darwin derivatives](https://en.wikipedia.org/wiki/Darwin_(operating_system)#Derived_projects), Phyllome OS **won't** offer support running macOS on non-Apple hardware.

### The Phyllome OS Project

The Phyllome OS Project relies on multiple tools, including the following front-facing tools: 

* **The wiki**: Have a look at the [wiki repository](https://github.com/PhyllomeOS/wiki) for more information on how you can contribute to improve the documentation.
* **Issues tracker**: public, read-only issue tracking is [available online](https://kanboard.phyllo.me/b/CH7qd98J2v7egmodk/development)
* **The website**: the website repository is [available here](https://github.com/PhyllomeOS/www) 
* **Code repository**: GitHub is being used

## Licence

* [GENERAL PUBLIC LICENCE 3](./LICENSE) 

## Acknowledgement

Thanks to the main contributors of the official Fedora kickstart files repository, and related tools:

> Adam Miller, Bastien Nocera, Bruno Wolff III, Bryan Kearney, Chitlesh Goorah, Christoph Wickert, 
Colin Walters, Fabian Affolter, Igor Pires Soares, Jens Petersen, Jeremy Katz, Jeroen van Meeuwen
Jesse Keating, Luya Tshimbalanga, Matthias Clasen, Pedro Silva, Rahul Sundaram, Sebastian Dziallas
Sebastian Vahl, wart. More information here : https://pagure.io/fedora-kickstarts