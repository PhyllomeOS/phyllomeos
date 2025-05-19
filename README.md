# Kickstart Phyllome OS

[Phyllome OS](https://wiki.phyllo.me/phyllomeos/context) uses the [kickstart installation method](https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#chapter-1-introduction) to deploy itself to a specific target computer or virtual machine by means of kickstart files.

This repository contains such files broken down as:

* `ingredients`🥑 🥥 🥭 🥝 🥦 🥬 🥒 🧄: the basic building blocks for assembling Phyllome OS and other derivatives.

* `recipes`🧾 🧩: lists of ingredients to compose several editions

* `dishes`🥨 🥐 🥖 🥧 🥞 🥯 🧆 🧁: read-to-consume and standalone kickstart artifacts, which can be used to deploy complete systems

Each ingredient represents a feature or a set of integrated features, such as a specific Desktop Environment or a storage configuration. 
    - Ingredients prefixed with *live* such as `live-core.cfg` are to be used with live editions only
    - *core* ingredients are meant be used in all their respective recipes, *base* ingredients, recommended but optional, and extra provides more stuff (sic)

## Development

Using a pull request, you can suggest a modification to an existing ingredient or create a new ingredient from scratch.

### Requirements

- `qemu`
- `libvirt`
- `virt-install`
- `pykickstart`

### Example 1: add a new package and include it into a recipe

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

#### Flatten

- Prepare the dish by following the recipe, a process called 'flattening'

```
$ ksflatten -c recipes/virtual-desktop-luanti.cfg -o dishes/virtual-desktop-luanti.cfg
```

> If any errors are detected, go back and fix them.

It is time to test the new dish!

- Navigate inside the `dishes` folder:

```
$ cd dishes/
```

#### Kickstart

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

### Example 2: Create a new recipe from the existing list of ingredients

The file `recipes/_list-of-ingredients.cfg` can be copied and edited to create your own remix of Phyllome OS, which itself is a remix of Fedora.

```
cp recipes/_list-of-ingredients.cfg recipes/my-new-distro.cfg
```

Then edit the said file to include your favorite ingredient

```
nano recipes/my-new-distro.cfg
```

```
#            __          ____                        ____  _____
#     ____  / /_  __  __/ / /___  ____ ___  ___     / __ \/ ___/
#    / __ \/ __ \/ / / / / / __ \/ __ `__ \/ _ \   / / / /\__ \
#   / /_/ / / / / /_/ / / / /_/ / / / / / /  __/  / /_/ /___/ /
#  / .___/_/ /_/\__, /_/_/\____/_/ /_/ /_/\___/   \____//____/
# /_/          /____/

# The list of ingredients for composing Phyllome OS
# Uncomment lines with "%include" to enable ingredient

# Installation method
# Exactly one option has to be picked
# %include ../ingredients/core.cfg # Text mode
# %include ../ingredients/live-core.cfg # For live systems only
# Documentation: https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#graphical-or-text-or-cmdline

# Storage configuration 
# Exactly one option has to be picked
# WARNING !!! Will erase local disks!
# %include ../ingredients/core-storage.cfg # Basic ext4 partition layout for UEFI-based systems
# %include ../ingredients/live-core-storage.cfg # For live systems only
# Documentation: https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html#part-or-partition
[...]
```

- Once you are done, you can [flatten](#flatten) the file and [kickstart](#kickstart) it as explained in the previous section.

## FAQ

If multiple dishes are affected by your ingredient, you can flatten them all

- Navigate to the recipes' directory

```
cd recipes
```

- Then use the following

```
for filename in *.cfg; do ksflatten -c "$filename" -o "../dishes/$filename"; done
```

The following message can safetly be ignored:

```
/usr/lib/python3.13/site-packages/pykickstart/commands/partition.py:461: KickstartParseWarning: A partition with the mountpoint / has already been defined.
```

## Acknowledgement

Thanks to the main contributors of the official Fedora kickstart files repository, and related tools:

> Adam Miller, Bastien Nocera, Bruno Wolff III, Bryan Kearney, Chitlesh Goorah, Christoph Wickert, Colin Walters, Fabian Affolter, Igor Pires Soares, Jens Petersen, Jeremy Katz, Jeroen van Meeuwen Jesse Keating, Luya Tshimbalanga, Matthias Clasen, Pedro Silva, Rahul Sundaram, Sebastian Dziallas Sebastian Vahl, wart. More information here : https://pagure.io/fedora-kickstarts