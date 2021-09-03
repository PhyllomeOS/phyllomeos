           __          ____                        ____  _____
    ____  / /_  __  __/ / /___  ____ ___  ___     / __ \/ ___/
   / __ \/ __ \/ / / / / / __ \/ __ `__ \/ _ \   / / / /\__ \
  / /_/ / / / / /_/ / / / /_/ / / / / / /  __/  / /_/ /___/ /
 / .___/_/ /_/\__, /_/_/\____/_/ /_/ /_/\___/   \____//____/
/_/          /____/

### What ? 

    * This repository contains kickstart files for Phyllome itself and its RPM-based guests.

### Examples

* With a remotely hosted kickstart file, install a minimal Linux RPM-based operating system automatically on an UEFI-based, Q35 PCI-Express virtual motherboard with virtio-devices.

Adjust settings according to your needs

```
virt-install \
    --name flat-dmd \ # [Optionnal] name of the machine 
    --connect qemu:///system \ # we connect to QEMU through the system socket ?
    --virt-type kvm \ # pick kvm VMM
    --arch x86_64 \ # x64 architecture
    --machine q35 \ # pci-express chipset enabled motherboard
    --boot uefi \ # boot type {bios;uefi?}
    --cpu host-model,topology.sockets=1,topology.cores=2,topology.threads=2 \
    --vcpus 4 \ # vCPU number
    --memory 8192 \ # 8192 Mb of RAM
    --controller type=scsi,model=virtio-scsi \
    --disk path=/var/lib/libvirt/images/flat-dmd.img,format=raw,bus=virtio,cache=writeback,size=10 \ # Create a 10 GiB RAW image
    --controller type=virtio-serial \ 
    --video virtio \ # virtual grahicard card, aka virtio-gpu 
    --network network=default,model=virtio \ # virtio NAT-based network
    --input type=keyboard,bus=virtio \ # virtio keyboard
    --input type=tablet,bus=virtio \ # virtio tablet/mouse
    --rng /dev/urandom,model=virtio \
    --channel spicevmc \ # use spice channel. Useful ?
    --autoconsole none \ # no auto connection to console on launch 
    --sound none \ no sound emulation
    --controller type=usb,model=none \ no emulated USB controller

    --location=https://download.fedoraproject.org/pub/fedora/linux/releases/34/Everything/x86_64/os/ \
    --extra-args="inst.ks=https://git.phyllo.me/home/kickstart/raw/branch/master/flat/flat-dmd.cfg"
```

###  Basic building blocks 

%include bmd.cfg # A minimal machine
%include bdmd.cfg # A desktop environment
%include bhmd.cfg # A base hypervisor
%include bhamd.cfg # Specific virtualization configuration for AMD (tm) CPUs

### Licence

* [GENERAL PUBLIC LICENCE 3](./LICENSE) 

### Acknowledgement

* Contributors of the official Fedora kickstart files repository, and direct inspiration for the automated, kickstart-based deployment : 

Adam Miller, Bastien Nocera, Bruno Wolff III, Bryan Kearney, Chitlesh Goorah, Christoph Wickert, 
Colin Walters, Fabian Affolter, Igor Pires Soares, Jens Petersen, Jeremy Katz, Jeroen van Meeuwen
Jesse Keating, Luya Tshimbalanga, Matthias Clasen, Pedro Silva, Rahul Sundaram, Sebastian Dziallas
Sebastian Vahl, wart. More information here : https://pagure.io/fedora-kickstarts

Thank you!