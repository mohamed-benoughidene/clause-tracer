#!/bin/bash
# After the run: desktop file, host WebKit really used (not bundled), clean removal.
set -u
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
rc=0
test -f /usr/share/applications/clause-tracer-trial.desktop && echo "desktop file present" || rc=1
command -v desktop-file-validate >/dev/null && { desktop-file-validate /usr/share/applications/clause-tracer-trial.desktop && echo "PASS: desktop-file-validate" || rc=1; }
find /opt/clause-tracer-trial -iname '*webkit2gtk*' -o -iname '*libgtk-3*' -o -iname '*libglib-2.0*' | tee bundled-libs.txt
if [ -s bundled-libs.txt ]; then echo "FAIL: host libs in the bundle"; rc=1; else echo "PASS: no webkit2gtk/gtk-3/glib shipped"; fi
$SUDO apt-get remove -y clause-tracer-trial >/dev/null
if dpkg -s clause-tracer-trial >/dev/null 2>&1 || [ -e /opt/clause-tracer-trial ] || [ -e /usr/bin/clause-tracer-trial ] || [ -e /usr/share/applications/clause-tracer-trial.desktop ]; then
  echo "FAIL: removal not clean"; rc=1
else
  echo "PASS: clean removal"
fi
exit $rc
