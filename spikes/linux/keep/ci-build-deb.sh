#!/bin/bash
# Build the frozen app and the .deb. Usage: ci-build-deb.sh t64|jammy  (run from the repo root,
# inside a venv that has pywebview and pyinstaller). Output: clause-tracer-trial_0.0.1~spike1_amd64.deb
set -eu
FLAVOUR="$1"
SPIKE_VARIANT=B pyinstaller --noconfirm spikes/linux/keep/trial.spec
ROOT=debroot
rm -rf "$ROOT"
mkdir -p "$ROOT/DEBIAN" "$ROOT/opt/clause-tracer-trial" "$ROOT/usr/bin" "$ROOT/usr/share/applications"
cp -a dist/clause-tracer-trial/. "$ROOT/opt/clause-tracer-trial/"
install -m 755 spikes/linux/keep/clause-tracer-trial.launcher "$ROOT/usr/bin/clause-tracer-trial"
install -m 644 spikes/linux/keep/clause-tracer-trial.desktop "$ROOT/usr/share/applications/clause-tracer-trial.desktop"
# Jammy (Ubuntu 22.04, Mint 21.x) predates the t64 transition.
if [ "$FLAVOUR" = jammy ]; then
  DEPENDS="libc6 (>= 2.35), libwebkit2gtk-4.1-0, gir1.2-webkit2-4.1, gir1.2-gtk-3.0, libgirepository-1.0-1, libglib2.0-0, libcairo2, libcairo-gobject2, libffi8, libssl3, libbz2-1.0, liblzma5, zlib1g, libexpat1, libuuid1"
else
  DEPENDS="libc6 (>= 2.38), libwebkit2gtk-4.1-0, gir1.2-webkit2-4.1, gir1.2-gtk-3.0, libgirepository-1.0-1, libglib2.0-0t64, libcairo2, libcairo-gobject2, libffi8, libssl3t64, libbz2-1.0, liblzma5, zlib1g, libexpat1, libuuid1"
fi
{
  printf 'Package: clause-tracer-trial\nVersion: 0.0.1~spike1\nArchitecture: amd64\n'
  printf 'Maintainer: Clause Tracer spike <spike@example.invalid>\nSection: utils\nPriority: optional\n'
  printf 'Depends: %s\n' "$DEPENDS"
  printf 'Description: Clause Tracer packaging trial (throwaway)\n'
  printf ' PyInstaller one-folder build of a pywebview GTK window that uses the\n'
  printf ' system WebKitGTK. Not a product.\n'
} > "$ROOT/DEBIAN/control"
dpkg-deb --build --root-owner-group "$ROOT" clause-tracer-trial_0.0.1~spike1_amd64.deb
dpkg-deb --info clause-tracer-trial_0.0.1~spike1_amd64.deb
