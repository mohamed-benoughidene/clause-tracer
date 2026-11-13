# PyInstaller spec for the Clause Tracer Linux spike (one-folder).
# Build:  SPIKE_VARIANT=B pyinstaller --noconfirm trial.spec
#   A  = PyInstaller defaults (no filtering)
#   A2 = force-bundle libwebkit2gtk/JSC/soup + their typelibs (to test a bundled WebKit)
#   B  = system WebKitGTK *and* system GTK/GLib stack: filter them out of the bundle.
#        B also needs use_host_gtk() in the app (resets PyInstaller GI env + LD_LIBRARY_PATH).
import os
import re

VARIANT = os.environ.get("SPIKE_VARIANT", "B")
HERE = os.path.abspath(SPECPATH)
PAGES = os.environ.get("SPIKE_PAGES", os.path.join(HERE, "pages-csp-eval"))

a = Analysis(
    [os.path.join(HERE, "trial_app.py")],
    pathex=[],
    binaries=[],
    datas=[(PAGES, "pages")],
    hiddenimports=["webview.platforms.gtk"],
    # pywebview pulls these in from system site-packages; the GTK backend does not need them.
    excludes=["cryptography", "bcrypt", "webview.platforms.qt", "webview.platforms.cef", "PyQt5", "PyQt6", "PySide6"],
    noarchive=False,
)

LIBDIR = "/usr/lib/x86_64-linux-gnu"
if VARIANT == "A2":
    for so in ("libwebkit2gtk-4.1.so.0", "libjavascriptcoregtk-4.1.so.0", "libsoup-3.0.so.0"):
        a.binaries.append((so, os.path.join(LIBDIR, so), "BINARY"))
    for tl in ("WebKit2-4.1", "JavaScriptCore-4.1", "Soup-3.0"):
        a.datas.append((f"gi_typelibs/{tl}.typelib", f"{LIBDIR}/girepository-1.0/{tl}.typelib", "DATA"))

if VARIANT == "B":
    # Shared libraries that must come from the host so they match the host's
    # WebKitGTK and its helper processes (WebKitWebProcess etc. inherit
    # LD_LIBRARY_PATH from the frozen app and would otherwise load our copies).
    SYSTEM_LIB = re.compile(
        r"^lib("
        r"webkit2gtk|javascriptcoregtk|soup-3|"                # WebKit itself
        r"gtk-3|gdk-3|gdk_pixbuf|atk|atk-bridge|atspi|"        # GTK 3 + a11y
        r"glib-2|gobject-2|gio-2|gmodule-2|girepository|"      # GLib + GI
        r"pango|pangocairo|pangoft2|cairo|cairo-gobject|harfbuzz|fontconfig|freetype|fribidi|"
        r"epoxy|X|xcb|wayland|xkbcommon|"                      # display stack
        r"stdc\+\+|gcc_s|ffi|z\.|"                             # toolchain runtime
        r"rsvg|cloudproviders|tinysparql|tracker|colord|lcms|"
        r"ssl|crypto|gnutls|nettle|hogweed|gmp|tasn1|idn2|unistring|p11-kit|"
        r"dbus|systemd|mount|blkid|selinux|pcre2|cap|"
        r"png|jpeg|tiff|webp|sharpyuv|jbig|lzma|zstd|bz2|brotli|deflate|Lerc|dav1d|"
        r"expat|xml2|graphite2|pixman|datrie|thai|"
        r"krb5|k5crypto|gssapi|com_err|keyutils|curl|nghttp|psl|rtmp|ssh|ldap|lber|sasl|"
        r"duktape|proxy|uuid|sqlite|gpg-error|gcrypt"
        r")"
    )

    # Host-side plug-ins (GIO modules, gdk-pixbuf loaders) also come from the host.
    SYSTEM_DIRS = ("gi_typelibs/", "share/", "lib/gdk-pixbuf", "gio_modules/", "etc/")
    # Leftovers pulled in only by those plug-ins (libproxy backend, ngtcp2) or that the
    # host libs need in the host's version (libatomic is used by libwebkit/libjsc).
    EXTRA = re.compile(r"^lib(pxbackend|ngtcp2|atomic)")

    def keep(entry):
        dest = entry[0]
        base = os.path.basename(dest)
        is_host_lib = bool(SYSTEM_LIB.match(base) or EXTRA.match(base))
        is_host_plugin = dest.startswith(SYSTEM_DIRS)
        return not (is_host_lib or is_host_plugin)

    a.binaries = [b for b in a.binaries if keep(b)]
    # Typelibs and GTK/GLib share data (schemas, icons, themes, locale) come from the host too.
    a.datas = [d for d in a.datas if not d[0].startswith(SYSTEM_DIRS)]

pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="clause-tracer-trial",
    debug=False, strip=False, upx=False, console=True,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="clause-tracer-trial")
