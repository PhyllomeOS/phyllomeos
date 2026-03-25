# Initial setup - generic wayland desktop mode

firstboot --enable # Initial Setup will start after the first reboot

%packages --exclude-weakdeps # Beginning of the packages section. Excludes weak package dependencies.

# TO BE TESTED -> initial-setup-gui # Graphical user interface for the initial-setup utility
# TO BE TESTED -> initial-setup-gui-wayland-generic.x86_64 # Run the initial-setup GUI in Wayland
gnome-initial-setup # Add GNOME initial setup too to let user create local account.

%end # End of the packages section
