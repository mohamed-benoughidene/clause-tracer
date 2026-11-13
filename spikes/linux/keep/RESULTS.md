# Clause Tracer Linux packaging spike: results

Machine: Debian 13 (trixie) amd64, kernel 6.12, no root. Everything ran inside
`bwrap` with an overlay on `/usr` (WebKitGTK .debs extracted with `dpkg-deb -x`,
never installed), under `xvfb-run`, with `--unshare-net`. See `run-in-sandbox.sh`.

## 0. Setup (session 2)

- `apt-get download` from deb.debian.org / security.debian.org (8 packages, 33.4 MB):
  libwebkit2gtk-4.1-0 2.54.0-1~deb13u3, libjavascriptcoregtk-4.1-0 2.54.0-1~deb13u3,
  gir1.2-webkit2-4.1 2.54.0-1~deb13u3, gir1.2-javascriptcoregtk-4.1 2.54.0-1~deb13u3,
  gir1.2-soup-3.0 3.6.5-3, libenchant-2-2 2.8.2+dfsg1-3, libhidapi-hidraw0 0.14.0-1+b2,
  libmanette-0.2-0 0.2.12-1. (The rest of `missing.txt` is spell-checker
  alternatives and unrelated virtual-package expansions, not needed.)
- venv with `--system-site-packages`; from PyPI: pywebview 6.2.1 (+ bottle 0.13.4,
  proxy_tools 0.1.0), pyinstaller 6.22.3, pyinstaller-hooks-contrib 2026.10.
  System: Python 3.13.5, PyGObject 3.50.0 (python3-gi).

## 1. Un-frozen app in the sandbox: PASS

`run-in-sandbox.sh stage -- venv/bin/python trial_app.py --pages pages-csp-eval`, rc=0.
WebKit runtime reported by GI: 2.54.0. js_api round trip: `before theme=light, after_set
theme=dark, read_back theme=dark`. All three processes (python3.13, WebKitNetworkProcess,
WebKitWebProcess) map `/usr/lib/x86_64-linux-gnu/libwebkit2gtk-4.1.so.0.24.3`.

## 2. Main question: build B (system WebKitGTK + GTK/GLib stack), first pass: PASS

`SPIKE_VARIANT=B pyinstaller trial.spec` (the saved filter), one-folder, 17M.
Run: `run-in-sandbox.sh stage -- distB/clause-tracer-trial/clause-tracer-trial`, rc=0, all checks
same as un-frozen (js_api round trip OK, page B reached, prefs read on B).
`/proc/<pid>/maps` of all three processes (frozen exe, WebKitNetworkProcess, WebKitWebProcess):
```
/usr/lib/x86_64-linux-gnu/libwebkit2gtk-4.1.so.0.24.3
/usr/lib/x86_64-linux-gnu/libjavascriptcoregtk-4.1.so.0.11.7
/usr/lib/x86_64-linux-gnu/libgtk-3.so.0.2417.32
/usr/lib/x86_64-linux-gnu/libglib-2.0.so.0.8400.4
/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.33
```
Helpers start from `/usr/lib/x86_64-linux-gnu/webkit2gtk-4.1/` and INHERIT
`LD_LIBRARY_PATH=<bundle>/_internal` from the frozen app (seen in `/proc/<pid>/environ`).
Gap in the saved filter: it filtered `a.datas` by path prefix, but `gio_modules/*.so` and
`lib/gdk-pixbuf/loaders/*.so` are in `a.binaries`, so they stayed in the bundle (plus
`libngtcp2*`, `libpxbackend-1.0.so`, `libatomic.so.1` pulled in by them). PyInstaller's GI
runtime hooks also point `GI_TYPELIB_PATH`, `GIO_MODULE_DIR`, `GDK_PIXBUF_MODULE_FILE`,
`GTK_PATH`, `GTK_DATA_PREFIX`, `GTK_EXE_PREFIX`, `PANGO_LIBDIR`, `XDG_DATA_DIRS` into the bundle.
Second pass fixes this (below).

### Build B, final: PASS (main question answered: yes)

Two workarounds were needed on top of the saved spec:
1. Spec filter now also drops `a.binaries` under `gio_modules/`, `lib/gdk-pixbuf`, and
   `libpxbackend*`, `libngtcp2*`, `libatomic*` (libwebkit2gtk NEEDs `libatomic.so.1`, so the
   host's copy must win). Bundle drops to 16M. Remaining .so in `_internal/` besides
   `python3.13/lib-dynload/*`: `libpython3.13.so.1.0`, `libreadline.so.8`, `libncursesw.so.6`,
   `libtinfo.so.6`, `gi/_gi*.so`, `tornado/speedups.abi3.so`.
2. Environment reset in the app before `import webview` (`use_host_gtk()` in `trial_app.py`):
   pop `GI_TYPELIB_PATH GIO_MODULE_DIR GDK_PIXBUF_MODULE_FILE GTK_PATH GTK_DATA_PREFIX
   GTK_EXE_PREFIX PANGO_LIBDIR PANGO_SYSCONFDIR`, strip the bundle from `XDG_DATA_DIRS`, and
   restore `LD_LIBRARY_PATH` from `LD_LIBRARY_PATH_ORIG` (or unset it).
   - Tried first as a PyInstaller custom runtime hook (`runtime_hooks=[...]`): OBSERVED that
     it runs BEFORE PyInstaller's built-in `pyi_rth_gi/gio/gdkpixbuf/gtk/glib` hooks, so the
     helpers still got `GIO_MODULE_DIR=<bundle>/gio_modules` etc. Dropped.
   - Without the `LD_LIBRARY_PATH` reset, WebKitWebProcess mapped `<bundle>/_internal/libtinfo.so.6`
     (seen in its `/proc/<pid>/maps`): bundle libraries leak into the system helpers.
   - With the reset: helpers' environ has `LD_LIBRARY_PATH` empty, no GTK vars, and
     `so_mapped_from_bundle: []` for both WebKitNetworkProcess and WebKitWebProcess.
     `GI_TYPELIB_PATH` empty in the app; GI finds the host typelibs from its default path.

Proof that libwebkit2gtk comes from the host (`LD_DEBUG=libs LD_DEBUG_OUTPUT=...`, rc=0):
```
9003: trying file=<bundle>/_internal/libwebkit2gtk-4.1.so.0      # frozen app, not found
9003: trying file=/lib/x86_64-linux-gnu/libwebkit2gtk-4.1.so.0
9003: calling init: /lib/x86_64-linux-gnu/libwebkit2gtk-4.1.so.0
9012: calling init: /lib/x86_64-linux-gnu/libwebkit2gtk-4.1.so.0  # WebKitNetworkProcess
9025: calling init: /lib/x86_64-linux-gnu/libwebkit2gtk-4.1.so.0  # WebKitWebProcess
9025: calling init: /usr/lib/x86_64-linux-gnu/webkit2gtk-4.1/injected-bundle/libwebkit2gtkinjectedbundle.so
```
(`/lib` is the merged-usr symlink to `/usr/lib`.) `/proc/<pid>/maps` in all three processes:
`/usr/lib/x86_64-linux-gnu/libwebkit2gtk-4.1.so.0.24.3`, `libjavascriptcoregtk-4.1.so.0.11.7`,
`libgtk-3.so.0.2417.32`, `libglib-2.0.so.0.8400.4`, `libsoup-3.0.so.0.7.4`, `libstdc++.so.6.0.33`.
All functional checks pass in B (js_api, page A to B, prefs on B).

### Build A (PyInstaller defaults) for comparison: runs here, but is the wrong design

`SPIKE_VARIANT=A`, run with `SPIKE_KEEP_PYI_ENV=1` (skips `use_host_gtk()`), rc=0, all
functional checks pass. Sizes (`du -sh`): **A = 241M** (of which `_internal/share` = 162M:
icons, themes, locale, mime, fontconfig, glib schemas), **B = 16M**.
- libwebkit2gtk / libjavascriptcoregtk / libsoup are NOT in A's folder, and A's
  `gi_typelibs/` has no `WebKit2-4.1` / `JavaScriptCore-4.1` / `Soup-3.0` typelib (PyInstaller's
  hooks did not collect them). So even A loads `/usr/lib/x86_64-linux-gnu/libwebkit2gtk-4.1.so.0.24.3`
  and the WebKit2 typelib from the host, and still starts the host's helpers from
  `/usr/lib/x86_64-linux-gnu/webkit2gtk-4.1/`.
- But A bundles GTK 3, GLib, cairo, pango, X11 libs, libstdc++, libgcc_s, libatomic, GIO modules
  (106 .so files at top level of `_internal/`), and through the inherited `LD_LIBRARY_PATH` the
  helpers map them: bundle .so files mapped = frozen app 91, WebKitNetworkProcess 74,
  WebKitWebProcess 76 (e.g. `_internal/libglib-2.0.so.0`, `_internal/libgtk-3.so.0`,
  `_internal/libstdc++.so.6` next to `/usr/.../libwebkit2gtk-4.1.so.0.24.3`).
- It works here only because the bundle was built on the same machine, so the versions match.
  INFERENCE: on a host whose WebKitGTK was built against a newer GLib/GTK/libstdc++ than the
  bundled copies, the host libwebkit and its helpers would load older bundled copies and can fail
  with missing symbols. A is a mixed stack; B is not.

**Right design: B** (bundle Python + app only; GTK/GLib/WebKitGTK/soup and their typelibs,
GIO modules, pixbuf loaders and share data from the host via `.deb Depends:`; reset the
PyInstaller GI env vars and `LD_LIBRARY_PATH` before GI starts).

## 3. Page A to page B navigation: PASS (old failure was a test bug, inference on cause)

Un-frozen, build B and build A all report `c_reached_b: true`, `c_api_ready_on_b: true`,
`c_prefs_on_b: {"theme": "dark", ...}` (set on A, read on B through js_api),
`c_b_script_ran: true`. Real file:// navigation works and `pywebview.api` is re-injected on B.
The old session-1 `runA` log shows `a_url = .../dist/trialA/pages/a.html` while every `run_js`
executed in `about:blank` (`document.getElementById('to-b')` null), i.e. page A itself never
loaded. INFERENCE: its start path pointed outside `_internal/` (where PyInstaller 6 puts
datas), so the load failed. The trial app now records `page_a_exists` and `a_doc_url`; both are
correct in all runs this session.

## 4. Other checks

### 4a. No listening TCP socket: PASS
In-app `ss -ltnpH` filtered by the app's process tree (app + both helpers), inside the
sandbox's own network namespace: un-frozen, A and B all give
`{"all_listening_lines": 0, "owned_by_app": []}` with `file://` URL + `http_server=False`.
Control (detector works): `--plain-path` (bare path instead of `file://` URL, still
`http_server=False`) gives `a_url = http://127.0.0.1:37704/a.html` and
`LISTEN 0 5 127.0.0.1:37704 ... users:(("python",pid=11500,fd=10))`.
**Differs from what the setting name suggests:** pywebview 6.2.1 starts its bottle server for
a bare local path even with `http_server=False`; pass a `file://` URL.

### 4b. fetch/XHR of other local files blocked, sibling assets load: PASS (with a caveat)
`webview.settings["ALLOW_FILE_URLS"] = False` (pywebview maps it to WebKit
`allow_file_access_from_file_urls`, gtk.py line 227). Every run:
`fetch('file:///etc/hostname')` -> `TypeError: Load failed`; XHR to it -> `status 0` error.
Sibling `<link rel=stylesheet>`, `<script src>` and `<img>` load (`css_color rgb(169, 18, 7)`,
`script_ran true`, `img_naturalWidth 4`). Caveat: `fetch('c.txt')` / XHR of a SIBLING file is
blocked too (`Load failed`), so pages cannot fetch their own JSON data; data must come through
js_api (fits the design) or be inlined as `<script src>`.

### 4c. Attempted https:// navigation: navigates IN the app window (FAIL as a safety property)
Clicking `<a href="https://example.org/">` (no `target`): `get_current_url()` ->
`https://example.org/`; `location.href` -> `about:blank` (load failed: sandbox has no
network). `pywebview` object still present. pywebview gtk.py `on_navigation` only sends
`target="_blank"` links to the browser when `OPEN_EXTERNAL_LINKS_IN_BROWSER` is on; same-frame
links are not intercepted. INFERENCE: with a network, the contract-reading window would show
the remote site. The app needs its own guard (e.g. connect to WebKit `decide-policy` and
`ignore()` any non-`file://` navigation, or open it with the system browser). NOT TESTED:
`target="_blank"` links, and such a guard.

### 4d. localStorage: not available with `private_mode=True` (by pywebview design)
`private_mode=True`: `ReferenceError: Can't find variable: localStorage`. pywebview gtk.py
sets `enable_html5_local_storage = False` and `enable_html5_database = False` in private mode
and uses `WebContext.new_ephemeral()`. With `SPIKE_PRIVATE=0` (`private_mode=False`):
`{"ok": true}`, but pywebview then keeps a cookie file under `~/.cache/<script name>/`.
Consequence for the design: keep theme/text size in Python via js_api (as planned); do not
plan on localStorage.

### 4e. CSP `<meta>` for file:// pages
| CSP | js_api | evaluate_js | violations |
|---|---|---|---|
| `default-src 'self'` | **broken** (`pywebview.api.get_prefs is not a function`) | EvalError | `script-src eval` x2, `style-src-elem inline` |
| `default-src 'self'; script-src 'self' 'unsafe-eval'` | works | 2 | `style-src-elem inline` (harmless here) |
| `default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'` | works | 2 | none |

Cause: pywebview injects its bridge with `evaluate_js`, which wraps code in
`eval("...")` (window.py line 463/477), and page CSP applies to that eval. The inline-style
violation is pywebview's own injected style. **Differs from a "strict CSP" reading of the
docs:** `'unsafe-eval'` is required for js_api on pywebview 6.2.1 GTK. Working value:
`default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'`.
Untried: a nonce/hash approach, or `'self'` without `'unsafe-eval'` plus a patched pywebview.

## 6. glibc floor (`objdump -T`, done before step 5 to fill `libc6 (>= ...)`)

Highest `GLIBC_` version needed by any file in the bundle:
- **B: GLIBC_2.38** (`libpython3.13.so.1.0`: `__isoc23_strtol`, `__isoc23_sscanf`, `fmod`...;
  also `libreadline.so.8`, `_curses`, `_decimal`). Nothing in B needs 2.39+.
- A: GLIBC_2.39 (bundled `libsystemd.so.0`), so A also raises the floor through bundled host libs.

Implication: the floor comes from the build machine's glibc via its Python (Debian 13's
python3.13 was built against glibc 2.41 headers, but only references up to 2.38 symbols).
Ubuntu 24.04 (2.39) and Debian 13 (2.41) are above 2.38, so this bundle would load there;
Ubuntu 22.04 / Mint 21 (2.35) would not. Rule for release builds: build on the OLDEST glibc
you support (e.g. an Ubuntu 22.04 or 24.04 build container), never on the newest. INFERENCE,
not tested: the bundled `gi/_gi*.so` is compiled against the build host's `libgirepository-1.0`
(PyGObject 3.50; PyGObject 3.51+ moves to `libgirepository-2.0`), so the PyGObject version and
the build distro also fix which girepository package the target needs.

## 5. Minimal .deb: PASS (built, extracted into the overlay, installed launcher ran)

`fakeroot dpkg-deb --build --root-owner-group debroot clause-tracer-trial_0.0.1~spike1_amd64.deb`
-> 7,102,456 bytes (xz). Contents: `/opt/clause-tracer-trial/` (build B), `/usr/bin/clause-tracer-trial`
(sh launcher: `exec /opt/clause-tracer-trial/clause-tracer-trial "$@"`),
`/usr/share/applications/clause-tracer-trial.desktop` (`desktop-file-validate`: no output, rc 0).
Cannot `dpkg -i` (no root), so: `dpkg-deb -x <deb> stage`, then
`run-in-sandbox.sh stage --opt stage/opt -- clause-tracer-trial` -> rc=0;
`command -v` -> `/usr/bin/clause-tracer-trial`; `start_url file:///opt/clause-tracer-trial/_internal/pages/a.html`;
js_api round trip OK; page B reached, prefs read on B; no listening socket; both helpers map
`/usr/lib/x86_64-linux-gnu/libwebkit2gtk-4.1.so.0.24.3`, `LD_LIBRARY_PATH` empty, no bundle .so mapped.
NOT TESTED: maintainer scripts, `dpkg -i` / apt dependency resolution, a desktop menu launch.

Final `Depends:` line:
```
Depends: libc6 (>= 2.38), libwebkit2gtk-4.1-0, gir1.2-webkit2-4.1, gir1.2-gtk-3.0, libgirepository-1.0-1, libglib2.0-0t64, libcairo2, libcairo-gobject2, libffi8, libssl3t64, libbz2-1.0, liblzma5, zlib1g, libexpat1, libuuid1
```
Justification (from `objdump -p` NEEDED of every file in the bundle, owners via `dpkg -S`):
- `libc6 (>= 2.38)`: glibc floor of the bundle (section 6); libc/libm/libdl/libpthread/ld-linux.
- `libwebkit2gtk-4.1-0`: the engine, and the helper binaries in `/usr/lib/x86_64-linux-gnu/webkit2gtk-4.1/`
  (pulls in libjavascriptcoregtk-4.1-0, libsoup-3.0-0, libgtk-3-0t64, libatomic1, bubblewrap ...).
- `gir1.2-webkit2-4.1`: **required, OBSERVED.** Typelibs are not bundled in B. Same .deb with
  `usr/lib/x86_64-linux-gnu/girepository-1.0/` (WebKit2-4.1, JavaScriptCore-4.1, Soup-3.0,
  WebKit2WebExtension-4.1) removed from the overlay: rc=1,
  `webview.errors.WebViewException: You must have either QT or GTK with Python extensions installed`.
  Its own Depends bring `gir1.2-javascriptcoregtk-4.1`, `gir1.2-soup-3.0`, `gir1.2-gtk-3.0`.
  So the library package alone is NOT enough.
- `gir1.2-gtk-3.0`: pywebview uses Gtk/Gdk through GI directly (already pulled by gir1.2-webkit2-4.1;
  listed because the app uses it directly). `libgtk-3-0t64` (Debian 13 name) itself comes through it and through
  libwebkit2gtk-4.1-0, so it is not listed separately.
- `libgirepository-1.0-1`, `libglib2.0-0t64`, `libffi8`: NEEDED by bundled `gi/_gi.cpython-313-*.so`.
- `libcairo2`, `libcairo-gobject2`: NEEDED by bundled `gi/_gi_cairo.cpython-313-*.so`.
- `libssl3t64` (`_ssl`), `libffi8` (`_ctypes`), `libbz2-1.0`, `liblzma5`, `zlib1g`, `libexpat1`, `libuuid1`:
  NEEDED by bundled Python / lib-dynload modules, deliberately left to the host by the spec filter.
Package names are Debian 13's; Ubuntu 24.04 uses the same t64 names (INFERENCE, not checked).

## 7. Clean-up: done

Removed venv, pip cache, downloaded .debs, staging roots, `debroot`, builds, the .deb, raw logs,
`saved/` (superseded by `keep/`), and the 12 throwaway `$HOME` dirs `run-in-sandbox.sh` made in
`/tmp/spikehome.*` (the script uses `mktemp` in `${TMPDIR:-/tmp}` and `exec`, so it cannot
delete them itself: set `TMPDIR` to a work folder next time). Proof:
```
$ ls -A linuxspike      -> keep
$ du -sh linuxspike     -> 220K
$ ls -d /tmp/spikehome.* | wc -l   -> 0
```
Nothing was installed; the git repo, `~/.config`, `~/.local` and system paths were not touched.

## Summary

| # | Check | Result |
|---|---|---|
| 1 | Un-frozen app runs in sandbox | PASS |
| 2 | Build B (system WebKitGTK + GTK/GLib) runs, loads `/usr/.../libwebkit2gtk-4.1.so.0.24.3` in app and both helpers | PASS (needs 2 workarounds) |
| 2 | Build A (defaults): runs here, but mixes bundled GTK/GLib/libstdc++ into the system helpers | runs; wrong design |
| 3 | file:// page A to B, `pywebview.api` on B, prefs set on A read on B | PASS (old failure: test bug, cause inferred) |
| 4a | No listening TCP socket with `file://` URL + `http_server=False` | PASS |
| 4b | fetch/XHR `file:///etc/hostname` blocked; sibling CSS/JS/img load | PASS (sibling fetch also blocked) |
| 4c | `https://` link | navigates in the app window; needs an app-side guard |
| 4d | localStorage | unavailable with `private_mode=True` (by pywebview design); works with `False` |
| 4e | CSP for file:// | needs `'unsafe-eval'` for js_api |
| 5 | .deb built, extracted into overlay, `/usr/bin` launcher runs | PASS |
| 5 | `gir1.2-webkit2-4.1` needed | YES (observed failure without it) |
| 6 | glibc floor | GLIBC_2.38 (B) |

**Answer to the main question:** yes. A PyInstaller 6.22.3 one-folder build of a pywebview 6.2.1
GTK app runs against the host's WebKitGTK 2.54.0, with the app and both helper processes loading
`/usr/lib/x86_64-linux-gnu/libwebkit2gtk-4.1.so.0.24.3`, PROVIDED (1) the GTK/GLib/WebKit stack, GI
typelibs, GIO modules, pixbuf loaders and share data are filtered out of the bundle, and (2) the app
undoes PyInstaller's GI environment variables and `LD_LIBRARY_PATH` before GI starts, because the
helpers inherit the environment.

### Exact versions
Python 3.13.5 (Debian system, bundled by PyInstaller); pywebview 6.2.1 (PyPI; bottle 0.13.4,
proxy_tools 0.1.0); PyInstaller 6.22.3 + pyinstaller-hooks-contrib 2026.10 (PyPI); PyGObject 3.50.0
(Debian python3-gi); WebKitGTK 2.54.0 (libwebkit2gtk-4.1-0 2.54.0-1~deb13u3, `.so.0.24.3`;
libjavascriptcoregtk `.so.0.11.7`); GTK 3.24.49-3 (`libgtk-3.so.0.2417.32`); GLib 2.84.4-3~deb13u5
(`libglib-2.0.so.0.8400.4`); libsoup 3.6.5 (`.so.0.7.4`); glibc 2.41-12+deb13u4 on the build host; libsoup-3.0-0 3.6.5-3.

### Final spec filter (variant B, in `keep/trial.spec`)
```python
SYSTEM_LIB = re.compile(r"^lib(webkit2gtk|javascriptcoregtk|soup-3|gtk-3|gdk-3|gdk_pixbuf|atk|atk-bridge|atspi|"
    r"glib-2|gobject-2|gio-2|gmodule-2|girepository|pango|pangocairo|pangoft2|cairo|cairo-gobject|harfbuzz|"
    r"fontconfig|freetype|fribidi|epoxy|X|xcb|wayland|xkbcommon|stdc\+\+|gcc_s|ffi|z\.|rsvg|cloudproviders|"
    r"tinysparql|tracker|colord|lcms|ssl|crypto|gnutls|nettle|hogweed|gmp|tasn1|idn2|unistring|p11-kit|dbus|"
    r"systemd|mount|blkid|selinux|pcre2|cap|png|jpeg|tiff|webp|sharpyuv|jbig|lzma|zstd|bz2|brotli|deflate|"
    r"Lerc|dav1d|expat|xml2|graphite2|pixman|datrie|thai|krb5|k5crypto|gssapi|com_err|keyutils|curl|nghttp|"
    r"psl|rtmp|ssh|ldap|lber|sasl|duktape|proxy|uuid|sqlite|gpg-error|gcrypt)")
SYSTEM_DIRS = ("gi_typelibs/", "share/", "lib/gdk-pixbuf", "gio_modules/", "etc/")
EXTRA = re.compile(r"^lib(pxbackend|ngtcp2|atomic)")
# drop from a.binaries: basename matches SYSTEM_LIB or EXTRA, or dest startswith SYSTEM_DIRS
# drop from a.datas: dest startswith SYSTEM_DIRS
```
plus `use_host_gtk()` at the top of `trial_app.py` (before `import webview`).

### Workarounds (all needed or found this session)
1. Filter `a.binaries` (not only `a.datas`) for `gio_modules/` and `lib/gdk-pixbuf`; drop
   `libpxbackend`, `libngtcp2`, `libatomic`.
2. Reset `GI_TYPELIB_PATH GIO_MODULE_DIR GDK_PIXBUF_MODULE_FILE GTK_PATH GTK_DATA_PREFIX
   GTK_EXE_PREFIX PANGO_LIBDIR PANGO_SYSCONFDIR`, strip the bundle from `XDG_DATA_DIRS`, and restore
   `LD_LIBRARY_PATH` from `LD_LIBRARY_PATH_ORIG`, in app code; a custom PyInstaller runtime hook runs
   too early (before the built-in GI hooks).
3. Pass a `file://` URL, not a bare path (a bare path starts a localhost server despite
   `http_server=False`).
4. CSP must allow `'unsafe-eval'` for js_api.
5. Load pages from `sys._MEIPASS` (`_internal/` in PyInstaller 6), not next to the executable
   (done in every frozen run this session; the failure without it is INFERRED from the old log).

### Where this differs from the pywebview docs / expectations
- `http_server=False` does not stop the local server when the URL is a bare file path.
- js_api injection uses `eval`, so a strict `default-src 'self'` CSP silently breaks `pywebview.api`.
- `private_mode=True` turns off localStorage/IndexedDB entirely (WebKit settings), not just persistence.
- `OPEN_EXTERNAL_LINKS_IN_BROWSER` only covers `target="_blank"`; ordinary links to `https://` load
  inside the window.
- `private_mode=False` writes cookies under `~/.cache/<script name>/`.
- `ALLOW_FILE_URLS=False` also blocks fetch/XHR of sibling files.

### Limits of this trial
- One machine: Debian 13 amd64, WebKitGTK files overlaid with bwrap (not installed through dpkg),
  under Xvfb (X11, `GDK_BACKEND=x11`), with no network (`--unshare-net`), and a throwaway HOME. No
  Wayland, no real desktop session, no GPU, no D-Bus session bus, no a11y bus.
- The bundle was built and run on the SAME distro, so the version-mismatch risk of build A, the
  glibc floor and the package names were argued from objdump/dpkg, not run on another distro.
  Ubuntu 22.04/24.04, Mint and Fedora (different package names, no .deb) NOT TESTED.
- `dpkg -i`/apt dependency resolution, maintainer scripts, a menu launch, `target="_blank"` links,
  and a navigation guard NOT TESTED.

## Files kept (`keep/`)
- `RESULTS.md`: this file.
- `trial_app.py`: self-checking pywebview app, with `use_host_gtk()`; env knobs `SPIKE_KEEP_PYI_ENV`,
  `SPIKE_PRIVATE`, `SPIKE_URL`; flags `--pages DIR`, `--plain-path`.
- `trial.spec`: PyInstaller spec, variants A / A2 / B (B = final filter).
- `run-in-sandbox.sh`: bwrap overlay + xvfb-run + no network + throwaway HOME.
- `deb-control`, `clause-tracer-trial.launcher`, `clause-tracer-trial.desktop`: .deb inputs.
- `deb-download-list.txt`: the 8 packages to `apt-get download` for the overlay.
- `pages/` (CSP `default-src 'self'`), `pages-csp-min/` (+ `'unsafe-eval'`),
  `pages-csp-eval/` (+ `'unsafe-eval'` and `style-src 'unsafe-inline'`; used for the builds).
- `logs/`: raw `RESULT=` lines of every run this session (work path shown as `$W`), and
  `lddebug-webkit-excerpt.txt`.
