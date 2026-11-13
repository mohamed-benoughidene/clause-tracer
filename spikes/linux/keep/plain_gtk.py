"""Plain PyGObject + WebKit2 4.1 check, no pywebview: can WebKitGTK show anything here?

Prints a timestamp when the window is mapped and when load-changed reaches FINISHED,
then quits. Exit 0 on FINISHED, 2 on the 30 s timeout.
"""
import sys
import time

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
from gi.repository import GLib, Gtk, WebKit2  # noqa: E402

T0 = time.time()
status = {"rc": 2}


def log(msg):
    print(f"[plain {time.time() - T0:6.2f}s] {msg}", flush=True)


log(f"WebKit {WebKit2.get_major_version()}.{WebKit2.get_minor_version()}.{WebKit2.get_micro_version()}")
win = Gtk.Window(title="plain")
win.set_default_size(400, 300)
view = WebKit2.WebView()
win.add(view)
win.connect("map-event", lambda *a: log("window mapped"))
view.connect("notify::is-web-process-responsive", lambda *a: log("web process responsive changed"))
view.connect("web-process-terminated", lambda v, reason: log(f"web process terminated: {reason}"))
view.connect("load-failed", lambda v, ev, uri, err: log(f"load-failed {uri}: {err.message}"))


def on_load(v, event):
    log(f"load-changed {event.value_nick}")
    if event == WebKit2.LoadEvent.FINISHED:
        status["rc"] = 0
        Gtk.main_quit()


view.connect("load-changed", on_load)
win.show_all()
log("show_all done")
view.load_html("<html><body><h1 id=x>hello</h1></body></html>", "about:blank")


def timeout():
    log("TIMEOUT after 30 s")
    Gtk.main_quit()
    return False


GLib.timeout_add_seconds(30, timeout)
Gtk.main()
log(f"exit rc={status['rc']}")
sys.exit(status["rc"])
