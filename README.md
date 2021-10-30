# Phyllome OS

> Virtualization for the rest of us

## What ? 

* This repository contains the basic building blocks required for deploying [Phyllome OS](https://phyllo.me/) bare-metal or in a virtual machine using [kickstart](https://en.wikipedia.org/wiki/Kickstart_(Linux)) files. 

## Development

For development purposes, Phyllome OS can be deployed in a virtual machine, leveraging nested-virtualization.

### Requirements

* A x86_64 platform that supports hardware-assisted virtualization
* A recent Linux Kernel (5.X)
* The `virt-install` and `virt-manager` tools
* `libvirt` and `qemu-kvm`up and running
* Nested-virtualization enabled

### Preparation

*Enable nested-virtualization* :

* For AMD-based systems

```to be done```

* For Intel-based systems

```to be done```

* For Fedora 34

*Install the prerequisites* :

```sudo dnf install -y qemu-kvm libvirt libvirt-daemon-config-network libvirt-daemon-kvm virt-install virt-top virt-manager libguestfs-tools python3-libguestfs guestfs-tools```

* For Ubuntu 20.4 or Debian 11

```To be done```

### Fire!

> Note : the following scripts relies on a kickstart tuned for Intel CPU and GPU, but may nonetheless on other systems.

This script will automatically deploy the alpha version of Phyllome OS, on a Q35 virtual motherboard, a UEFI-based firmware, virtio-devices accross the board, 2 vCPUs, 4 GB of RAM and a disk of 5 GB. 

Adjust it according to your need. When ready, copy and paste it to your terminal and fire-up it up!

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
    --disk path=/var/lib/libvirt/images/flat-dhimd.img,format=raw,bus=virtio,cache=writeback,size=5 \
    --location=https://download.fedoraproject.org/pub/fedora/linux/releases/34/Everything/x86_64/os/ \
    --extra-args="inst.ks=https://git.phyllo.me/home/kickstart/raw/branch/master/flat/flat-dhimd.cfg"
```

### Licence

* [GENERAL PUBLIC LICENCE 3](./LICENSE) 

### Acknowledgement

* I would like to thanks the main contributors of the official Fedora kickstart files repository, and related tools. 

> Adam Miller, Bastien Nocera, Bruno Wolff III, Bryan Kearney, Chitlesh Goorah, Christoph Wickert, 
Colin Walters, Fabian Affolter, Igor Pires Soares, Jens Petersen, Jeremy Katz, Jeroen van Meeuwen
Jesse Keating, Luya Tshimbalanga, Matthias Clasen, Pedro Silva, Rahul Sundaram, Sebastian Dziallas
Sebastian Vahl, wart. More information here : https://pagure.io/fedora-kickstarts