#            __          ____                        ____  _____
#     ____  / /_  __  __/ / /___  ____ ___  ___     / __ \/ ___/
#    / __ \/ __ \/ / / / / / __ \/ __ `__ \/ _ \   / / / /\__ \
#   / /_/ / / / / /_/ / / / /_/ / / / / / /  __/  / /_/ /___/ /
#  / .___/_/ /_/\__, /_/_/\____/_/ /_/ /_/\___/   \____//____/
# /_/          /____/

# GNOME desktop packages

%packages --exclude-weakdeps # Beginning of the packages section. Excludes weak package dependencies

@base-graphical
## provides the following as mandatory packages:
# mesa-dri-drivers
# mesa-vulkan-drivers
# plymouth-system-theme

# @critical-path-gnome not using this group but hand-picking packages 
## Mandatory packages found in hidden `@critical-path-gnome` group (`dnf group info --hidden critical-path-gnome`)
## Not using 
## provides the following as mandatory packages:
bash-color-prompt # Color prompt for bash shell
dconf # A configuration system
gdm # The GNOME Display Manager
# gnome-classic-session # GNOME "classic" mode session
gnome-control-center # Utilities to configure the GNOME desktop
# gnome-initial-setup # Bootstrapping your OS
gnome-shell # Window management and application launching for GNOME
gvfs-fuse # FUSE support for gvfs
# ptyxis # A container oriented terminal for GNOME
### and the following as default packages
# NetworkManager-pptp # NetworkManager VPN plugin for PPTP
# avahi # Local network service discovery
# gnome-bluetooth # Bluetooth graphical utilities
gnome-session-wayland-session # Desktop file for wayland based gnome session
# gnome-software # A software center for GNOME
nautilus # File manager for GNOME
# toolbox # Tool for interactive command line environments on Linux

## Extra hand-picked packages
gnome-backgrounds.noarch # wallpapers from the GNOME project
gnome-terminal # Terminal emulator for GNOME
dejavu-sans-mono-fonts # the gnome-shell package doesn't include much fonts by default, resulting in weird spacings in GNOME Terminal. GNOME Terminal unfortunately doesn't automatically pick this font 
firefox # Mozilla Firefox Web browser
mozilla-ublock-origin.noarch # An efficient blocker for Firefox

pipewire-alsa # PipeWire media server ALSA support
pipewire-pulseaudio # PipeWire PulseAudio implementation
pipewire-jack-audio-connection-kit # PipeWire JACK implementation

%end # End of the packagages section
