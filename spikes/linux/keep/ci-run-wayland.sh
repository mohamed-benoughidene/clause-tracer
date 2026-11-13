#!/bin/bash
# Run a command under a HEADLESS WAYLAND compositor (weston), with no X server at all.
# Usage: ci-run-wayland.sh LOGFILE command args...   Optional: NO_DBUS=1 skips dbus-run-session.
# Extra variables (LIBGL_ALWAYS_SOFTWARE, WEBKIT_DISABLE_DMABUF_RENDERER) pass through from the caller.
LOG="$1"; shift
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
echo "==== diagnostics before run ===="
id; head -3 /etc/os-release; weston --version 2>&1 | head -1
echo "--- env (filtered)"; env | grep -viE "token|secret|key|password" | sort
export XDG_RUNTIME_DIR; XDG_RUNTIME_DIR="$(mktemp -d /tmp/xdg-wl.XXXXXX)"; chmod 700 "$XDG_RUNTIME_DIR"
unset DISPLAY XAUTHORITY
export WAYLAND_DISPLAY=wl-test GDK_BACKEND=wayland XDG_SESSION_TYPE=wayland
export PYWEBVIEW_LOG=debug G_MESSAGES_DEBUG=all NO_AT_BRIDGE=1 SPIKE_DIAG=1
echo "--- no X server: sockets in /tmp/.X11-unix:"; ls /tmp/.X11-unix 2>&1; pgrep -a 'Xorg|Xvfb|Xwayland' || echo "(no X process)"
echo "==== start weston ===="
WPID=""
for args in "--backend=headless --renderer=pixman" "--backend=headless" "--backend=headless-backend.so --use-pixman" "--backend=headless-backend.so"; do
  echo "try: weston $args"
  weston $args --socket=wl-test --idle-time=0 >"$LOG.weston" 2>&1 &
  WPID=$!
  for i in $(seq 1 50); do [ -S "$XDG_RUNTIME_DIR/wl-test" ] && break; kill -0 $WPID 2>/dev/null || break; sleep 0.2; done
  [ -S "$XDG_RUNTIME_DIR/wl-test" ] && { echo "weston up with: $args"; break; }
  kill $WPID 2>/dev/null; WPID=""; tail -5 "$LOG.weston"
done
[ -n "$WPID" ] || { echo "FAIL: no weston"; exit 0; }
echo "==== run ===="
START=$(date +%s)
set +e
if [ -n "${NO_DBUS-}" ]; then WRAP=""; else WRAP="dbus-run-session --"; fi
$WRAP "$@" 2>&1 \
  | while IFS= read -r l; do printf '%s %s\n' "$(date +%T.%N | cut -c1-12)" "$l"; done | tee "$LOG"
echo "run took $(( $(date +%s) - START )) s"
kill $WPID 2>/dev/null
echo "==== weston log (tail) ===="; tail -15 "$LOG.weston"
sed -E 's/^[0-9:.]+ (RESULT=)/\1/' "$LOG" > "$LOG.clean"
exit 0
