# Kickstart Phyllome OS

[Phyllome OS](https://wiki.phyllo.me/phyllomeos/context) uses the [kickstart installation method](https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#chapter-1-introduction) to deploy itself to a specific target computer or virtual machine by means of kickstart files.

This repository contains such files broken down as:

* `ingredients`🥑 🥥 🥭 🥝 🥦 🥬 🥒 🧄: the basic building blocks for assembling Phyllome OS and other derivatives.

* `recipes`🧾 🧩: lists of ingredients to compose several editions

* `dishes`🥨 🥐 🥖 🥧 🥞 🥯 🧆 🧁: read-to-consume and standalone kickstart artifacts, which can be used to deploy complete systems

## Development

Using a pull request, you can suggest a modification to an existing ingredient or create a new ingredient from scratch.

### Example: add a new package and include it into a recipe

- Add [Luanti](https://www.luanti.org/), a free and open-source sandbox video game engine formerly known as Minetest, as a standalone ingredient, using the `echo` command

```
echo "%packages --exclude-weakdeps # Beginning of the package section. Does not include weak dependencies

luanti # Multiplayer infinite-world block sandbox with survival mode

%end # End of the packages section" > ingredients/extra-luanti.cfg
```

Instead of creating a recipe from scratch, let's make a copy of the `virtual-desktop.cfg` recipe, which provide a Desktop environment necessary for *luanti* to function

```
$ cp recipes/virtual-desktop.cfg recipes/virtual-desktop-luanti.cfg
```

- Add the extra ingredient to the new recipe:

``` 
echo "%include ../ingredients/extra-luanti.cfg # Sandbox video game engine" >> recipes/virtual-desktop-luanti.cfg
```

- Prepare the dish by following the recipe, a process called 'flattening'

```
$ ksflatten -c recipes/virtual-desktop-luanti.cfg -o dishes/virtual-desktop-luanti.cfg
```

> If any errors are detected, go back and fix them.

If multiple dishes are affected by your ingredient, you can flatten them all

- Navigate to the recipes' directory

```
cd recipes
```

- Then use the following

```
for filename in *.cfg; do ksflatten -c "$filename" -o "../dishes/$filename"; done
```

The following message can be discarded:

```
/usr/lib/python3.13/site-packages/pykickstart/commands/partition.py:461: KickstartParseWarning: A partition with the mountpoint / has already been defined.
```

It is time to test the new dish!

- Navigate inside the `dishes` folder:

```
$ cd ../dishes/
```

* You can then kickstart your own installation:

```
# virt-install \
    --connect qemu:///system     \
    --metadata description="Virtual desktop with Luanti" \
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
    --disk path=/var/lib/libvirt/images/virtual-desktop-luanti.img,format=raw,bus=virtio,cache=writeback,size=10 \
    --location=https://download.fedoraproject.org/pub/fedora/linux/releases/42/Everything/x86_64/os/ \
    --initrd-inject virtual-desktop-luanti.cfg --extra-args "inst.ks=file:virtual-desktop-luanti.cfg"
```

- When the installation is done, the machine will shut down

- Start it again, and ensure that Luanti has correctly been installed

That's it !

## Acknowledgement

Thanks to the main contributors of the official Fedora kickstart files repository, and related tools:

> Adam Miller, Bastien Nocera, Bruno Wolff III, Bryan Kearney, Chitlesh Goorah, Christoph Wickert, Colin Walters, Fabian Affolter, Igor Pires Soares, Jens Petersen, Jeremy Katz, Jeroen van Meeuwen Jesse Keating, Luya Tshimbalanga, Matthias Clasen, Pedro Silva, Rahul Sundaram, Sebastian Dziallas Sebastian Vahl, wart. More information here : https://pagure.io/fedora-kickstarts