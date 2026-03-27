# GNOME desktop post-installation configuration

%post --nochroot --log=/mnt/sysimage/root/gnome-desktop-post.log # Beginning of %post section. Those commands are executed outside the chroot environment

cat >> /mnt/sysimage/usr/share/glib-2.0/schemas/org.gnome.desktop.media-handling.gschema.override<< EOF
[org.gnome.desktop.media-handling]
automount-open=false
autorun-never=true
EOF

cat >> /mnt/sysimage/usr/share/glib-2.0/schemas/org.gnome.Terminal.gschema.override<< EOF
[org.gnome.Terminal.Legacy.Profile]
font='DejaVu Sans Mono 12'
use-system-font=false
auditable-bell=false
EOF

cat >> /mnt/sysimage/usr/share/glib-2.0/schemas/org.gnome.desktop.wm.preferences.gschema.override<< EOF
[org.gnome.desktop.wm.preferences]
button-layout=':minimize,maximize,close'
EOF

cat >> /mnt/sysimage/usr/share/glib-2.0/schemas/org.gnome.desktop.a11y.gschema.override<< EOF
[org.gnome.desktop.a11y]
always-show-universal-access-status=true
EOF

cat >> /mnt/sysimage/usr/share/glib-2.0/schemas/org.gnome.desktop.interface.gschema.override<< EOF
[org.gnome.desktop.interface]
enable-animations=false
EOF

cat >> /mnt/sysimage/usr/share/glib-2.0/schemas/org.gnome.desktop.privacy.gschema.override<< EOF
[org.gnome.desktop.privacy]
remove-old-temp-files=true
remember-recent-file=false
remember-app-usage=false
disable-camera=true
disable-microphone=true
disable-sound-output=true
EOF

cat >> /mnt/sysimage/usr/share/glib-2.0/schemas/org.gnome.desktop.search-providers.gschema.override<< EOF
[org.gnome.desktop.search-providers]
disable-external=true
EOF

cat >> /mnt/sysimage/usr/share/glib-2.0/schemas/org.gnome.desktop.notifications.gschema.override<< EOF
[org.gnome.desktop.notifications.application]
enable-sound-alerts=false
EOF

cat >> /mnt/sysimage/usr/share/glib-2.0/schemas/org.gnome.desktop.sound.gschema.override<< EOF
[org.gnome.desktop.sound]
event-sounds=false
EOF

cat >> /mnt/sysimage/usr/share/glib-2.0/schemas/org.gnome.desktop.thumbnailers.gschema.override<< EOF
[org.gnome.desktop.thumbnailers]
disable-all=true
EOF

glib-compile-schemas /mnt/sysimage/usr/share/glib-2.0/schemas/

%end # End of the %post section
