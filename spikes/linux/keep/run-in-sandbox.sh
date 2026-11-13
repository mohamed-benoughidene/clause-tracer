#!/bin/sh
# Run a command with extra .deb contents overlaid on /usr (and /opt), rootless.
# Usage: run-in-sandbox.sh STAGING_ROOT [--opt OPT_DIR] -- command args...
# STAGING_ROOT holds usr/ from `dpkg-deb -x` of the WebKitGTK packages.
# Runs under Xvfb (xvfb-run -a) with a throwaway HOME so nothing touches ~/,
# and with --unshare-net so the trial page cannot reach the network.
set -eu
STAGE=$(realpath "$1"); shift
OPTARGS=""
if [ "${1:-}" = "--opt" ]; then OPTARGS="--overlay-src /opt --overlay-src $(realpath "$2") --tmp-overlay /opt"; shift 2; fi
[ "${1:-}" = "--" ] && shift
FAKEHOME=$(mktemp -d "${TMPDIR:-/tmp}/spikehome.XXXXXX")
# Extra usr/bin from a .deb (launcher) is overlaid as part of STAGE/usr.
# shellcheck disable=SC2086
exec env -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS \
  HOME="$FAKEHOME" XDG_CONFIG_HOME="$FAKEHOME/.config" XDG_CACHE_HOME="$FAKEHOME/.cache" \
  XDG_DATA_HOME="$FAKEHOME/.local/share" XDG_STATE_HOME="$FAKEHOME/.local/state" \
  BROWSER=/bin/true NO_AT_BRIDGE=1 GDK_BACKEND=x11 \
  xvfb-run -a -s "-screen 0 1024x768x24" \
  bwrap --dev-bind / / \
    --overlay-src /usr --overlay-src "$STAGE/usr" --tmp-overlay /usr \
    $OPTARGS \
    --unshare-net --die-with-parent -- "$@"
