# Phyllome OS

Phyllome OS is a [Fedora Remix](https://fedoraproject.org/wiki/Remix) designed to leverage [hardware-assisted virtualization](https://wiki.phyllo.me/virt/lexicon#hardware-assisted-virtualization) and [paravirtualization](https://wiki.phyllo.me/virt/lexicon#paravirtualization) to make it easier to run modern guest operating systems locally.

Phyllome OS uses the [automated kickstart installation](https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#chapter-1-introduction) method to deploy itself to a specific target.

This repository contains complete or partial kickstart files, [organized by folders](#the-content-of-this-repository), for Phyllome OS and also a handful of other operating systems artifacts. 

> Phyllome OS is in its ***alpha*** stage of development. Expect bugs and disappointment

## The content of this repository


Each version of Phyllome OS is a `dish` that is based on a `recipe` that lists `ingredients`. 

* `ingredients`🥑 🥥 🥭 🥝 🥦 🥬 🥒 🧄...: this directory contains the basic building blocks, or ingredients, for assembling Phyllome OS and other derivatives.
    * Each ingredient represents a feature or a set of integrated features, such as a particular Desktop Environment. 
* `recipes`🧾 🧩: this directory contains recipes, which are made of ingredients.
* `dishes`🥨 🥐 🥖 🥧 🥞 🥯 🧆 🧁...: this directory contains the end-product in the form of stand-alone and ready-to-consume kickstart file, just like a ready to eat dish.

## Development

Let's assume you wish to add [Luanti](https://www.luanti.org/), a free and open-source sandbox video game engine, as an ingredient to a dish.

* Clone this repository and move inside:

```
$ git clone https://git.phyllo.me/roots/phyllomeos && cd phyllomeos
```

* Make a copy of the `template.cfg` file and rename it

```
$ cp ingredients/template.cfg ingredients/extra-luanti.cfg
```

* Add software `luanti` to your file:

```
$ nano ingredients/extra-luanti.cfg
```

```
# What ? This partial kickstart file provides the video game Minetest

%packages --exclude-weakdeps # Beginning of the packages section. Excludes weak package dependencies

luanti # a free and open-source sandbox video game

%end
```

* Navigate inside the `recipes` folder:

```
$ cd recipes
```

* Pick a suitable recipe to add your ingredient to it. As luanti is a GUI application, `virtual-desktop.cfg` is a fitting candidate. Make a copy of it.

```
$ cp virtual-desktop.cfg virtual-desktop-lunanti.cfg
```

* Edit the file and add the newly defined ingredient:

```
$ nano virtual-desktop-luanti.cfg
```

```
%include ../ingredients/base-fedora-repo.cfg # offical repositories for Fedora
%include ../ingredients/base-storage.cfg # base storage
%include ../ingredients/base.cfg # A minimal machine
%include ../ingredients/base-desktop-gnome.cfg # A desktop environment
%include ../ingredients/base-guest-agents.cfg # Guest agents
%include ../ingredients/base-initial-setup-gnome.cfg # Includes initial-setup for GNOME Shell, allowing for the creation of a user after the first boot, as well as some basic configuration

%include ../ingredients/extra-luanti.cfg # A free and open-source sandbox video game

poweroff # Shut down the system after a successful installation
```

* Merge the kickstart basic building blocks a single file, or dish. This process is called 'flattening'.

```
$ ksflatten -c virtual-desktop-lunanti.cfg -o ../dishes/virtual-desktop-luanti.cfg
```

> If any errors are detected, go back and fix them.

* Navigate inside the `dishes` folder:

```
$ cd ../dishes/
```

* You can then kickstart your own installation:

```
# virt-install \
    --connect qemu:///system \
    --metadata description="Phyllome OS Desktop, virtual edition, with Luanti" \
    --os-variant fedora41 \
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
    --location=https://download.fedoraproject.org/pub/fedora/linux/releases/42/Everything/x86_64/os/ \
    --initrd-inject virtual-desktop-luanti.cfg --extra-args "inst.ks=file:virtual-desktop-luanti.cfg"
```

## Acknowledgement

Thanks to the main contributors of the official Fedora kickstart files repository, and related tools:

> Adam Miller, Bastien Nocera, Bruno Wolff III, Bryan Kearney, Chitlesh Goorah, Christoph Wickert, Colin Walters, Fabian Affolter, Igor Pires Soares, Jens Petersen, Jeremy Katz, Jeroen van Meeuwen Jesse Keating, Luya Tshimbalanga, Matthias Clasen, Pedro Silva, Rahul Sundaram, Sebastian Dziallas Sebastian Vahl, wart. More information here : https://pagure.io/fedora-kickstarts