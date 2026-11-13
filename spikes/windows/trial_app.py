"""Clause Tracer packaging trial: self-checking pywebview app (Windows variant of the Linux trial).

Loads pages/a.html by absolute file:// URL, runs a list of checks through
run_js / evaluate_js, prints one JSON line prefixed RESULT= and closes itself.

Usage: trial_app.py [--plain-path] [--pages DIR]
  --plain-path  pass a bare absolute path instead of a file:// URL (shows that
                pywebview then starts its local HTTP server even with
                http_server=False).
"""

import importlib.metadata
import json
import os
import subprocess
import sys
import threading
import time


def use_host_gtk():
    """Frozen build only: let the host's GTK/GLib/WebKitGTK stack configure itself.

    PyInstaller's GI runtime hooks point these variables into the bundle and its
    bootloader sets LD_LIBRARY_PATH to the bundle. WebKitWebProcess and
    WebKitNetworkProcess inherit the environment, so undo both before any GI/GTK use.
    A PyInstaller custom runtime hook is too early: it runs before the built-in ones.
    glibc reads LD_LIBRARY_PATH once at start, so this process is not affected.
    """
    if not getattr(sys, "frozen", False) or os.environ.get("SPIKE_KEEP_PYI_ENV"):
        return
    meipass = sys._MEIPASS
    for k in ("GI_TYPELIB_PATH", "GIO_MODULE_DIR", "GDK_PIXBUF_MODULE_FILE", "GTK_PATH",
              "GTK_DATA_PREFIX", "GTK_EXE_PREFIX", "PANGO_LIBDIR", "PANGO_SYSCONFDIR"):
        os.environ.pop(k, None)
    xdg = [p for p in os.environ.get("XDG_DATA_DIRS", "").split(os.pathsep) if p and not p.startswith(meipass)]
    os.environ["XDG_DATA_DIRS"] = os.pathsep.join(xdg or ["/usr/local/share", "/usr/share"])
    orig = os.environ.pop("LD_LIBRARY_PATH_ORIG", None)
    if orig:
        os.environ["LD_LIBRARY_PATH"] = orig
    else:
        os.environ.pop("LD_LIBRARY_PATH", None)


if sys.platform.startswith("linux"):
    use_host_gtk()

import webview  # noqa: E402

HERE = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
OTHER_FILE = "file:///C:/Windows/win.ini" if os.name == "nt" else "file:///etc/hostname"


class Api:
    """Preferences live in Python, not in the page (pages reload on navigation)."""

    def __init__(self):
        self._prefs = {"theme": "light", "text_size": "normal"}

    def get_prefs(self):
        return dict(self._prefs)

    def set_prefs(self, theme):
        self._prefs["theme"] = str(theme)
        return dict(self._prefs)


def descendants(pid):
    import psutil
    return [pid] + [c.pid for c in psutil.Process(pid).children(recursive=True)]


def proc_info(pid):
    import psutil
    try:
        p = psutil.Process(pid)
        return {"pid": pid, "name": p.name()}
    except Exception as e:  # noqa: BLE001
        return {"pid": pid, "error": repr(e)}


def listening_sockets(pids):
    import psutil
    mine = []
    for c in psutil.net_connections(kind="inet"):
        if c.status == psutil.CONN_LISTEN and c.pid in pids:
            mine.append(f"{c.laddr.ip}:{c.laddr.port} pid={c.pid}")
    return {"owned_by_app": mine}


def main_checks(window, results):
    def js(body):
        """Run a JS function body via run_js (no eval wrapper); return parsed JSON."""
        raw = window.run_js("JSON.stringify((function(){" + body + "})())")
        try:
            return json.loads(raw)
        except Exception:
            return {"raw": raw}

    def wait_for(body, timeout=15):
        end = time.time() + timeout
        while time.time() < end:
            v = js(body)
            if v is True:
                return True
            time.sleep(0.2)
        return False

    def run_async(name, body, timeout=10):
        """body is an async function body; result is stashed in window.__r[name]."""
        js(
            "window.__r = window.__r || {};"
            f"(async function(){{{body}}})().then(v => window.__r['{name}'] = v,"
            f" e => window.__r['{name}'] = {{error: String(e)}}); return 1;"
        )
        end = time.time() + timeout
        while time.time() < end:
            v = js(f"return (window.__r || {{}})['{name}'] === undefined ? '__pending' : window.__r['{name}'];")
            if v != "__pending":
                return v
            time.sleep(0.2)
        return "timeout"

    try:
        api_ready = "return !!(window.pywebview && window.pywebview.api && typeof window.pywebview.api.get_prefs === 'function');"
        results["a_url"] = window.get_current_url()
        results["a_doc_url"] = js("return document.URL;")
        results["a_api_ready"] = wait_for(api_ready)
        # (a) js_api round trip
        results["a_roundtrip"] = run_async(
            "rt",
            "const p0 = await pywebview.api.get_prefs();"
            "const p1 = await pywebview.api.set_prefs('dark');"
            "const p2 = await pywebview.api.get_prefs();"
            "return {before: p0, after_set: p1, read_back: p2};",
        )
        # (a') does pywebview's evaluate_js (eval wrapper) work under this CSP?
        try:
            results["a_evaluate_js_1plus1"] = window.evaluate_js("1+1")
        except Exception as e:  # noqa: BLE001
            results["a_evaluate_js_1plus1"] = f"error: {type(e).__name__}: {e}"
        # (b) sibling CSS, JS, image
        results["b_assets"] = js(
            "const img = document.getElementById('logo');"
            "return {css_color: getComputedStyle(document.getElementById('probe')).color,"
            " script_ran: window.siblingScriptRan === true,"
            " img_complete: img.complete, img_naturalWidth: img.naturalWidth,"
            " csp_violations: window.cspViolations || 'listener-not-installed'};"
        )
        # (f) localStorage
        results["f_localStorage"] = js(
            "try { localStorage.setItem('k','v'); return {ok: localStorage.getItem('k') === 'v'}; }"
            " catch (e) { return {ok: false, error: String(e)}; }"
        )
        # (d) fetch/XHR to other local files
        results["d_fetch_etc_hostname"] = run_async(
            "f1", "try { const r = await fetch('' + OTHER_FILE + ''); return {ok: true, status: r.status, len: (await r.text()).length}; } catch (e) { return {blocked: true, error: String(e)}; }"
        )
        results["d_fetch_sibling"] = run_async(
            "f2", "try { const r = await fetch('c.txt'); return {ok: true, text: (await r.text()).trim()}; } catch (e) { return {blocked: true, error: String(e)}; }"
        )
        results["d_xhr_sibling"] = run_async(
            "x1",
            "return await new Promise(res => { const x = new XMLHttpRequest();"
            " try { x.open('GET', 'c.txt'); x.onload = () => res({ok: true, status: x.status, text: x.responseText.trim()});"
            " x.onerror = () => res({blocked: true, status: x.status}); x.send(); } catch (e) { res({blocked: true, error: String(e)}); } });",
        )
        results["d_xhr_etc_hostname"] = run_async(
            "x2",
            "return await new Promise(res => { const x = new XMLHttpRequest();"
            " try { x.open('GET', '' + OTHER_FILE + ''); x.onload = () => res({ok: true, len: x.responseText.length});"
            " x.onerror = () => res({blocked: true, status: x.status}); x.send(); } catch (e) { res({blocked: true, error: String(e)}); } });",
        )
        results["csp_violations_on_a_final"] = js("return window.cspViolations || null;")
        # process tree, loaded libs, listening sockets (while window is up)
        pids = descendants(os.getpid())
        results["procs"] = [proc_info(p) for p in pids]
        results["listen"] = listening_sockets(pids)
        # (c) navigate to b.html by clicking the link
        js("document.getElementById('to-b').click(); return 1;")
        results["c_reached_b"] = wait_for("return location.pathname.endsWith('b.html');")
        results["c_url"] = window.get_current_url()
        results["c_api_ready_on_b"] = wait_for(api_ready)
        results["c_prefs_on_b"] = run_async("pb", "return await pywebview.api.get_prefs();")
        results["c_b_script_ran"] = js("return window.pageBScriptRan === true;")
        # (e) attempt https navigation (no network needed; we only report)
        js("document.getElementById('to-web').click(); return 1;")
        time.sleep(4)
        results["e_url_after_https_click"] = window.get_current_url()
        results["e_doc_location"] = js("return location.href;")
        results["csp_violations_on_b"] = js("return window.cspViolations || null;")
        results["e_api_still_present"] = js("return !!(window.pywebview && window.pywebview.api);")
    except Exception as e:  # noqa: BLE001
        results["exception"] = f"{type(e).__name__}: {e}"
    finally:
        print("RESULT=" + json.dumps(results, sort_keys=True, indent=1), flush=True)
        r = results
        verdict = {
            "api_round_trip": isinstance(r.get("a_roundtrip"), dict) and (r["a_roundtrip"].get("read_back") or {}).get("theme") == "dark",
            "assets_load": isinstance(r.get("b_assets"), dict) and r["b_assets"].get("script_ran") is True and (r["b_assets"].get("img_naturalWidth") or 0) > 0,
            "no_listening_socket": r.get("listen", {}).get("owned_by_app") == [],
            "link_to_page_b": r.get("c_reached_b") is True and r.get("c_api_ready_on_b") is True,
            "prefs_survive_navigation": isinstance(r.get("c_prefs_on_b"), dict) and r["c_prefs_on_b"].get("theme") == "dark",
            "other_local_file_blocked": isinstance(r.get("d_fetch_etc_hostname"), dict) and r["d_fetch_etc_hostname"].get("blocked") is True,
        }
        print("VERDICT=" + json.dumps(verdict, indent=1), flush=True)
        ok = all(verdict.values())
        print("RESULT pages:", "PASS" if ok else "FAIL", flush=True)
        window.destroy()
        os._exit(0 if ok else 1)


def main():
    plain = "--plain-path" in sys.argv
    pages = os.path.join(HERE, "pages")
    if "--pages" in sys.argv:
        pages = os.path.abspath(sys.argv[sys.argv.index("--pages") + 1])
    page_a = os.path.join(pages, "a.html")
    import pathlib
    url = page_a if plain else pathlib.Path(page_a).as_uri()
    if os.environ.get("SPIKE_URL"):
        url = os.environ["SPIKE_URL"]

    webview.settings["ALLOW_FILE_URLS"] = False  # maps to WebKit allow_file_access_from_file_urls
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = True

    results = {
        "python": sys.version.split()[0],
        "frozen": bool(getattr(sys, "frozen", False)),
        "pywebview": importlib.metadata.version("pywebview"),
        "start_url": url,
        "page_a_exists": os.path.isfile(page_a),
    }
    window = webview.create_window("Clause Tracer trial", url, js_api=Api(), width=800, height=600)
    t = threading.Timer(60, lambda: os._exit(3))  # hard stop if anything hangs
    t.daemon = True
    t.start()
    webview.start(main_checks, (window, results), gui="gtk" if sys.platform.startswith("linux") else None, http_server=False, private_mode=os.environ.get("SPIKE_PRIVATE", "1") == "1")


if __name__ == "__main__":
    main()
