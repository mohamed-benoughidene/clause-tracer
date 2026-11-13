#!/bin/bash
# Install the .deb plus the tools the checks need. Usage: ci-install.sh DEB [cross]
# cross = the .deb was built on another release; if apt refuses it, say why and then
# force-install it so the run shows what would fail at run time.
DEB="$1"; CROSS="${2-}"
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
export DEBIAN_FRONTEND=noninteractive
$SUDO apt-get update -qq
$SUDO apt-get install -y xvfb xauth dbus dbus-x11 iproute2 desktop-file-utils python3-minimal weston
if $SUDO apt-get install -y "./$DEB"; then
  echo "INSTALL: apt OK"
  exit 0
fi
echo "INSTALL: apt FAILED for ./$DEB"
[ -n "$CROSS" ] || exit 1
echo "--- why (simulate)"; $SUDO apt-get install --simulate "./$DEB" 2>&1 | tail -15
$SUDO apt-get install -y libwebkit2gtk-4.1-0 gir1.2-webkit2-4.1 gir1.2-gtk-3.0 || true
$SUDO dpkg -i --force-depends "$DEB" && echo "INSTALL: forced with --force-depends (unmet dependencies ignored)"
exit 0
