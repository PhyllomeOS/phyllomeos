# Phyllome OS

[Phyllome OS](#phyllome-os) is a [Fedora Remix](https://fedoraproject.org/wiki/Remix) designed to leverage [hardware-assisted virtualization](https://wiki.phyllo.me/virt/lexicon#hardware-assisted-virtualization) and [paravirtualization](https://wiki.phyllo.me/virt/lexicon#paravirtualization) to make it easier to run modern guest operating systems locally.

Phyllome OS uses the kickstart installation method to deploy itself to a specific target.

[The kickstart installation method](https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#chapter-1-introduction) provides a way to configure and automate the installation of most [RPM-based distributions](https://en.wikipedia.org/wiki/Category:RPM-based_Linux_distributions), including [the official Fedora distributions](https://pagure.io/fedora-kickstarts) as well as Fedora Remixes like Phyllome OS.

This repository contains complete or partial kickstart files, [organized by folders](#the-content-of-this-repository).

> Phyllome OS is in its ***alpha*** stage of development. Expect bugs and disappointment.

## Kickstarting Phyllome OS

Kickstarting Phyllome OS in a virtual machine (VM) using a kickstart file is a great way to test it out before using [burning the ISO](https://github.com/PhyllomeOS/phyllomeos/releases/tag/v.0.2.0-alpha) or commiting to [a bare-metal installation](https://wiki.phyllo.me/deploy/prepare).

It is also the first step kickstart files.

* **Requirements:**
    * An x86_64 platform with hardware-assisted virtualization [enabled](https://wiki.phyllo.me/deploy/prepare#enable-hardware-assisted-virtualization)
    * A Linux distribution with a recent Linux kernel (> 5.X), such as Ubuntu 22.04 or Fedora 38

### Initial steps

1. Enable **nested-virtualization**

    * On *AMD*-based systems:

    ```
    # echo "options kvm_amd nested=1" >> /etc/modprobe.d/kvm.conf
    ```

    * On *Intel*-based systems:
    
    ```
    # echo "options kvm_intel nested=1" >> /etc/modprobe.d/kvm.conf`
    ```

* Then `reboot` and verify that nested-virtualization is activated, using the following command, which should return a `1` or `Y`:

    * For *AMD*-based systems:
    
    ```
    # cat /sys/module/kvm_amd/parameters/nested    
    1
    ```

    * For *Intel*-based systems:

    ```
    # cat /sys/module/kvm_intel/parameters/nested    
    1
    ```

2. Install dependencies 

    * For Fedora 35 and up

    ```
    # dnf install -y qemu-kvm libvirt libvirt-daemon-config-network libvirt-daemon-kvm virt-install virt-top virt-manager libguestfs-tools python3-libguestfs guestfs-tools pykickstart wget
    ```

    * For Ubuntu 22.04

    ```
    # apt install qemu-kvm qemu-utils libvirt-daemon-system libvirt-clients bridge-utils virt-manager ovmf python-pykickstart wget
    ```

3. Add current user to the libvirt group

```
# usermod -a -G libvirt $(whoami)
```

### Kickstart Phyllome OS

* Fetch the kickstart file optimized for deploying Phyllome OS in a virtual machine:

```
$ wget https://raw.githubusercontent.com/PhyllomeOS/phyllomeos/main/dishes/virtual-phyllome-desktop.cfg
```

* Use `virt-install` alongside the previously downloaded kickstart file and use it to automatically bootstrap Phyllome OS on a virtual machine with 2 vCPUs, 4 GB of RAM and a disk of 5 GB (feel free to increase these values which satisfy the minimal requirements for Phyllome OS):

```
# virt-install \
    --connect qemu:///system \
    --metadata description="Phyllome OS Desktop, virtual edition" \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name virtual-phyllome-desktop \
    --boot uefi \
    --cpu host-model,topology.sockets=1,topology.cores=2,topology.threads=1 \
    --vcpus 2 \
    --memory 4096 \
    --video virtio \
    --graphics spice,listen=none \
    --channel spicevmc \
    --autoconsole none \
    --console pty,target.type=virtio \
    --sound none \
    --network type=user,model=virtio \
    --controller type=virtio-serial \
    --controller type=usb,model=none \
    --controller type=scsi,model=virtio-scsi \
    --input type=keyboard,bus=virtio \
    --input type=tablet,bus=virtio \
    --rng /dev/urandom,model=virtio \
    --disk path=/var/lib/libvirt/images/virtual-phyllome-desktop.img,format=raw,bus=virtio,cache=writeback,size=5 \
    --location=https://download.fedoraproject.org/pub/fedora/linux/releases/38/Everything/x86_64/os/ \
    --initrd-inject virtual-phyllome-desktop.cfg --extra-args "inst.ks=file:virtual-phyllome-desktop.cfg"
```
* The following message will appear, and the installation process will be launched behind the scenes:

```
Starting install...
Retrieving file vmlinuz...                                  |  10 MB  00:00     
Retrieving file initrd.img...                               |  79 MB  00:02     
Allocating 'virtinst-inlu7cmw-vmlinuz'                      |  10 MB  00:00     
Transferring virtinst-inlu7cmw-vmlinuz                      |  10 MB  00:00     
Allocating 'virtinst-2dd8ghse-initrd.img'                   |  79 MB  00:00     
Transferring virtinst-2dd8ghse-initrd.img                   |  79 MB  00:01     
Allocating 'virtual-phyllome-desktop.img'                   | 5.0 GB  00:00     

Domain is still running. Installation may be in progress.
You can reconnect to the console to complete the installation process.
```

* Open `virt-manager` to view the virtual machine console to follow the process (**View** > **Console**). Eventually, you will be greeted with this screen:

![greetings](./img/greetings.png)

* After you are done setting up your user account, `virt-manager` will automatically start:

![greetings](./img/desktop.png)

* Provided that the virtual machine has enough resources, you can repeat the last steps to automatically deploy Phyllome OS inside Phyllome OS

## The content of this repository

This repository contains snippets of code for the [multiple versions](https://wiki.phyllo.me/deploy/rightforyou#phyllome-os-versions) of Phyllome OS, and also a handful of other operating systems artefacts. 

Each version of Phyllome OS is like a `dish` that is based on a `recipe` that lists `ingredients`. 

* `ingredients`🥑 🥥 🥭 🥝 🥦 🥬 🥒 🧄...: this directory contains the basic building blocks, or ingredients, for assembling Phyllome OS and other derivatives.
    * Each ingredient represents a feature or a set of integrated features, such as a particular Desktop Environment. Not all ingredients will end up in the final product, but that is okay to try and add new flavors!
    * Feel free to add new ingredients here, such as another Desktop Environment or a new set of software. 
* `recipes`🧾 🧩: this directory contains recipes, which are made of ingredients listed in a specific order.
    * Everyone is free to create a new recipe based on new or existing ingredients.
* `dishes`🥨 🥐 🥖 🥧 🥞 🥯 🧆 🧁...: this directory contains the end-product in the form of stand-alone and ready-to-consume kickstart files, just like cooked dishes.
    * When a new ingredient ends up in a dish, it should be tested before being committed to the repository. The total number of official dishes should not exceed a handful, to avoid the burden of testing too many dishes.
* `post-first-startup-scripts` : this directory contains scripts that are meant to be run manually by the user after a successful installation. This is like the topping of a dish.
    * These code snippets will eventually be included inside existing building blocks, summoned as a systemd unit after a successful installation, or turned into RPM-packages.
* `img` : this directory contains screenshots of Phyllome OS used in the README file.

## Improve an existing or create your own OS artefact

Let's assume your want to add [Minetest](https://minetest.org/), a free and open-source sandbox video game, as an ingredient to a dish, so that you could deploy a virtual machine with this specific package:

* Clone this repository using `git`:

```
$ git clone https://github.com/PhyllomeOS/PhyllomeOS.git
```

* Make a copy of the `template.cfg` partial kickstart, and append `extra` to its name such as in `extra-minetest.cfg`:

```
$ cp ingredients/template.cfg ingredients/extra-minetest.cfg
```

* Add software `minetest` to your file:

```
$ nano ingredients/extra-minetest.cfg
```

```
# What ? This partial kickstart file provides the video game Minetest

%packages --exclude-weakdeps # Beginning of the packages section. Excludes weak package dependencies

minetest # a free and open-source sandbox video game

%end
```

* Pick a suitable recipe to add your ingredient to it. As Minetest is a GUI application, `virtual-desktop.cfg` is a fitting candidate. Make a copy of it.

```
$ cp recipes/virtual-desktop.cfg recipes/virtual-desktop-minetest.cfg
```

* Edit the file and add the newly defined ingredient:

```
$ nano recipes/virtual-desktop-minetest.cfg
```

```
%include ../ingredients/base-fedora-repo.cfg # offical repositories for Fedora
%include ../ingredients/base-storage.cfg # base storage
%include ../ingredients/base.cfg # A minimal machine
%include ../ingredients/base-desktop-gnome.cfg # A desktop environment
%include ../ingredients/base-guest-agents.cfg # Guest agents
%include ../ingredients/base-initial-setup-gnome.cfg # Includes initial-setup for GNOME Shell, allowing for the creation of a user after the first boot, as well as some basic configuration

%include ../ingredients/extra-minetest.cfg # A free and open-source sandbox video game

poweroff # Shut down the system after a successful installation
```

* Then, merge the kickstart basic building blocks a single file, or dish. This process is called 'flattening'.

```
$ ksflatten -c recipe/virtual-desktop-minetest.cfg -o ../dishes/virtual-desktop-minetest.cfg
```

> If any errors are detected, go back and fix them.

* You can then kickstart your own installation:

```
# virt-install \
    --connect qemu:///system \
    --metadata description="Phyllome OS Desktop, virtual edition" \
    --os-variant detect=off \
    --virt-type kvm \
    --arch x86_64 \
    --machine q35 \
    --name virtual-desktop-minetest \
    --boot uefi \
    --cpu host-model,topology.sockets=1,topology.cores=2,topology.threads=1 \
    --vcpus 2 \
    --memory 4096 \
    --video virtio \
    --graphics spice,listen=none \
    --channel spicevmc \
    --autoconsole none \
    --console pty,target.type=virtio \
    --sound none \
    --network type=user,model=virtio \
    --controller type=virtio-serial \
    --controller type=usb,model=none \
    --controller type=scsi,model=virtio-scsi \
    --input type=keyboard,bus=virtio \
    --input type=tablet,bus=virtio \
    --rng /dev/urandom,model=virtio \
    --disk path=/var/lib/libvirt/images/virtual-phyllome-desktop.img,format=raw,bus=virtio,cache=writeback,size=5 \
    --location=https://download.fedoraproject.org/pub/fedora/linux/releases/38/Everything/x86_64/os/ \
    --initrd-inject virtual-desktop-minetest.cfg --extra-args "inst.ks=file:virtual-desktop-minetest.cfg"
```

## The goal of Phyllome OS

Phyllome OS goal is to maximize ease-of-use and compatibility. As such, it intends to become the easiest way to use modern operating systems locally, in a virtual machine, by integrating pertinent open-source software such as `libvirt`, `qemu-kvm` (and eventually `Cloud Hypervisor`), as well as `virt-manager`.

Users should not have to manage Phyllome OS: they should be able to pick their favorite operating system and Phyllome OS should run it, no questions asked.

> Note : expect for open-source [Darwin derivatives](https://en.wikipedia.org/wiki/Darwin_(operating_system)#Derived_projects), Phyllome OS **strongly** discourages users from running proprietary, darwin-based derivatives on non-Apple hardware.

### The Phyllome OS Project

> External contributions to Phyllome OS are welcome. Have a look [here](https://kanboard.phyllo.me/b/CH7qd98J2v7egmodk/development) for some ideas on what to do next, or feel free to create a GitHub issue and suggest an idea you wish to work on. Also, it might be good to skim through the [white-paper](https://files.phyllo.me/s/oYwfxYpZcbppwr6) to understand what it is about and what the project is trying to achieve.

The Phyllome OS Project relies on multiple tools, including the following public-facing tools: 

* **Wiki**: Take a look at the [wiki repository](https://github.com/PhyllomeOS/wiki) for more information on how you can contribute to improving the documentation.
* **Issues tracker**: a public, read-only issue tracking is [available online](https://kanboard.phyllo.me/b/CH7qd98J2v7egmodk/development). From now on, GitHub issue tracking will be used to track development-only issues.  
* **Code repository**: GitHub is used to host the code

## Licenses

* [MIT](./LICENSE.md) for the most part, alongside [GPL](./blocks-live/LICENSE.md)-licensed code.

## Acknowledgement

Thanks to the main contributors of the official Fedora kickstart files repository, and related tools:

> Adam Miller, Bastien Nocera, Bruno Wolff III, Bryan Kearney, Chitlesh Goorah, Christoph Wickert, Colin Walters, Fabian Affolter, Igor Pires Soares, Jens Petersen, Jeremy Katz, Jeroen van Meeuwen Jesse Keating, Luya Tshimbalanga, Matthias Clasen, Pedro Silva, Rahul Sundaram, Sebastian Dziallas Sebastian Vahl, wart. More information here : https://pagure.io/fedora-kickstarts