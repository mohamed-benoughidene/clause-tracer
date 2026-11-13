#!/bin/bash
# What does the D-Bus / portal / systemd-user situation look like right now?
echo "--- uid=$(id -u) XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR-<unset>} DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS-<unset>}"
ls -la "/run/user/$(id -u)/" 2>&1 | head -30
echo "--- user bus socket"; ls -la "/run/user/$(id -u)/bus" 2>&1
echo "--- loginctl"; loginctl list-sessions 2>&1 | head; loginctl show-user "$(id -un)" 2>&1 | head -12
echo "--- systemctl --user"; systemctl --user is-system-running 2>&1 | head -3
systemctl --user status xdg-desktop-portal.service --no-pager 2>&1 | head -15
systemctl --user list-units --no-pager 2>&1 | head -30
echo "--- busctl --user list"; busctl --user list --no-pager 2>&1 | head -20
echo "--- portal packages"; dpkg -l | grep -E "xdg-desktop-portal|dbus" | awk '{print $2, $3}'
