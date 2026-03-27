# Kickstart Phyllome OS

[Phyllome OS](https://wiki.phyllo.me/phyllomeos/context) uses the [kickstart installation method](https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#chapter-1-introduction) to deploy itself to a specific target computer or virtual machine by means of kickstart files.

Provided that some dependencies are met (`libvirt` is running on your computer, QEMU is installed, etc), one could run the following script to deploy virtual machines, including Phyllome OS itself.

- :

```
```

- Execute it and pick `virtual-desktop-hypervisor` when prompted:

```
./deploy-vm.sh

Executing: ./deploy/core-count.sh
System has more than 2 core (nproc --all: 6).
[...]
10. virtual-desktop-hypervisor
[...]
Enter the number of the file you want to select: 10
You selected: virtual-desktop-hypervisor

Starting install...
Retrieving 'vmlinuz'                                                                                     |  16 MB  00:00:00     
Retrieving 'initrd.img'                                                                                  | 161 MB  00:00:05     
Allocating 'virtinst-n0km88yy-vmlinuz'                                                                   |  16 MB  00:00:00     
Transferring 'virtinst-n0km88yy-vmlinuz'                                                                 |  16 MB  00:00:00     
Allocating 'virtinst-qxr2jxcb-initrd.img'                                                                | 161 MB  00:00:00     
Transferring 'virtinst-qxr2jxcb-initrd.img'                                                              | 161 MB  00:00:00     
Allocating 'virtual-desktop-hypervisor.img'                                                              |  10 GB  00:00:00     
Creating domain...                              
```
After a successfull installation, the virtual machine will shutdown and be ready to use when powered on again.

## Repository structure

This repository contains such files broken down as:

* `ingredients`🥑 🥥 🥭 🥝 🥦 🥬 🥒 🧄: the basic building blocks for assembling Phyllome OS and other derivatives.

* `recipes`🧾 🧩: lists of ingredients to compose several editions

* `dishes`🥨 🥐 🥖 🥧 🥞 🥯 🧆 🧁: read-to-consume and standalone kickstart artifacts, which can be used to deploy complete systems

Each ingredient represents a feature or a set of integrated features, such as a specific Desktop Environment or a storage configuration. 
    - Ingredients prefixed with *live* such as `live-core.cfg` are to be used with live editions only
    - *core* ingredients are meant be used in all their respective recipes, *base* ingredients, recommended but optional, and extra provides more stuff (sic)

