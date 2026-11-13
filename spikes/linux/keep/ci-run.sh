#!/bin/bash
# Run a command under dbus-run-session + xvfb-run with full diagnostics.
# Usage: ci-run.sh LOGFILE command args...   (stdout+stderr both go to LOGFILE and the console)
# Never fails the step itself: the caller checks the log.
LOG="$1"; shift
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
echo "==== diagnostics before run ===="
echo "--- id"; id
echo "--- XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR-<unset>}  DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS-<unset>}"
echo "--- kernel / userns"; uname -a
sysctl kernel.unprivileged_userns_clone kernel.apparmor_restrict_unprivileged_userns user.max_user_namespaces 2>&1 || true
echo "--- os-release"; head -3 /etc/os-release
echo "--- env"; env | grep -viE "token|secret|key|password" | sort
echo "==== run ===="
export PYWEBVIEW_LOG=debug G_MESSAGES_DEBUG=all NO_AT_BRIDGE=1 GDK_BACKEND=x11
export SPIKE_DIAG=1
START=$(date +%s)
set +e
if [ -n "${NO_DBUS-}" ]; then WRAP=""; else WRAP="dbus-run-session --"; fi
$WRAP xvfb-run -a -s "-screen 0 1280x1024x24" "$@" 2>&1 \
  | while IFS= read -r l; do printf '%s %s\n' "$(date +%T.%N | cut -c1-12)" "$l"; done | tee "$LOG"
echo "run took $(( $(date +%s) - START )) s"
if ! grep -q '^[0-9:.]* RESULT=' "$LOG"; then
  echo "==== no RESULT line: kernel messages (AppArmor / userns denials) ===="
  $SUDO dmesg 2>&1 | tail -50 || true
  $SUDO journalctl -k --no-pager 2>&1 | tail -30 || true
fi
# strip the timestamp prefix from RESULT= so the checker finds it
sed -E 's/^[0-9:.]+ (RESULT=)/\1/' "$LOG" > "$LOG.clean"
exit 0
