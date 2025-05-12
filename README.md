# Kickstart Phyllome OS

[Phyllome OS](https://wiki.phyllo.me/phyllomeos/context) uses the [kickstart installation method](https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#chapter-1-introduction) to deploy itself to a specific target computer or virtual machine by means of kickstart files.

This repository contains such files broken down as:

* `ingredients`🥑 🥥 🥭 🥝 🥦 🥬 🥒 🧄: the basic building blocks for assembling Phyllome OS and other derivatives.

* `recipes`🧾 🧩: lists of ingredients to compose several editions

* `dishes`🥨 🥐 🥖 🥧 🥞 🥯 🧆 🧁: read-to-consume and standalone kickstart artifacts, which can be used to deploy complete systems

## Development

git clone 

You can suggest a modification to an existing ingredient or create a new ingredient from scratch.

Let's assume that you wish to add *luanti*, an infinite-world block sandbox engine to all default installation. 

The following command will automatically add the said package to the file `ingredient/core-packages-default.cfg`, just before the `%end` packages section

`sed -i '/^%end # End of the packages section/i luanti # Multiplayer infinite-world block sandbox with survival mode' ingredient/core-packages-default.cfg`

A recipe can then be modified. 

### Recipes

You can modify an existing recipe or create

Let's assume you wish to add [Luanti](https://www.luanti.org/), a free and open-source sandbox video game engine, as an ingredient to a dish.

* Clone this repository and change directory:

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
# What ? This partial kickstart file provides the video game Luanti

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

If multiple dishes are affected by your ingredients, flatten them all while in the `recipes` folder.

```
for filename in *.cfg; do ksflatten -c "$filename" -o "../dishes/$filename"; done
```

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
    --name virtual-desktop-luanti \
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