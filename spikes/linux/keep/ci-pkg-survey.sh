#!/bin/bash
# Print what this distro ships for the trial's dependencies. Read-only apart from apt-get update.
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
echo "--- os-release"; cat /etc/os-release | head -6
echo "--- glibc"; ldd --version | head -1
$SUDO apt-get update -qq
for p in libwebkit2gtk-4.1-0 gir1.2-webkit2-4.1 libwebkit2gtk-4.0-37 gir1.2-webkit2-4.0 libwebkitgtk-6.0-4 gir1.2-webkit-6.0 \
         gir1.2-gtk-3.0 libgtk-3-0t64 libgtk-3-0 libgirepository-1.0-1 libgirepository-2.0-0 gir1.2-girepository-2.0 \
         python3-gi python3-gi-cairo libglib2.0-0t64 libglib2.0-0 libssl3t64 libssl3 libc6 python3 weston cage sway xvfb; do
  echo "=== $p"; apt-cache policy "$p" | sed -n '1,3p'
done
echo "--- python3-gi depends"; apt-cache depends python3-gi | head -20
echo "--- libwebkit2gtk-4.1-0 depends (first 25)"; apt-cache depends libwebkit2gtk-4.1-0 2>&1 | head -25
echo "--- search"; apt-cache search --names-only 'libwebkit2gtk|gir1.2-webkit|libgirepository' | sort
