# ADR-0009: Wrap the engine in pywebview, talk over stdio, ship one-dir with Inno Setup

**Status:** Accepted (12 Nov 2026)
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
[Spec 9](../spec.md) builds a command-line tool first, then wraps it as a desktop app with an installer for Linux and Windows. The Windows installer is built by GitHub Actions and tested in a Windows virtual machine. Before this decision, Spec 13 listed the desktop shell as open, framed as "Tauri or Electron". [ADR 0004](0004-code-layout.md) says the shell gets its own folder and ADR.

The [pipeline architecture report](../../reports/Clause%20Tracer%20pipeline%20architecture.md) compared Tauri, Electron, PySide6, pywebview and Briefcase, and left the engine transport open. [The v1 design decisions report](../../reports/Clause%20Tracer%20v1%20design%20decisions.md) decided the question by who can review the code. The developer reviews only Python and has no Windows machine. The HTML prototype already exists. Spec 8.1 allows no telemetry and no outbound host beyond OpenRouter and GitHub.

## Decision
The project owner accepted the following on 12 Nov 2026. It replaces Spec 13's "Tauri or Electron" framing.

- **Shell.** pywebview 6.x, reusing the HTML prototype. The Qt backend stays as a Linux escape hatch only.
- **UI to Python.** The UI calls `window.pywebview.api`, a narrow Python `js_api` facade.
- **Engine.** The facade spawns the same frozen executable with a `serve --stdio` sub-command. They exchange newline-delimited JSON carrying `protocol_version`. Cancel is a message, then terminate after a timeout. The child exits at end-of-file on stdin; on Windows, a Job Object with kill-on-close also guards it.
- **Packaging.** PyInstaller one-dir. Inno Setup on GitHub's `windows-latest` runner, carrying or fetching the WebView2 bootstrapper.
- **Signing.** Release unsigned first, with published checksums. Then buy an individual OV certificate (about $99 a year) if the developer is outside the US and Canada.
- **Windows testing.** Build, silently install and drive the real WebView2 window in CI with Playwright for Python over CDP. A Windows 11 Enterprise 90-day evaluation VM under QEMU/KVM covers the manual SmartScreen and installer look.
- **Front-end tests.** pytest and Playwright for Python against the static pages with a fake `window.pywebview.api`, in Chromium and WebKit. One real-app smoke test under Xvfb on Linux.

## Options Considered

### Option A: pywebview, stdio child, PyInstaller one-dir, Inno Setup (chosen)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: a Python facade, a child process and an installer script |
| Cost | Bundle size dominated by the NER model; start-up not measured |
| Scalability | Single user, not a scale question |
| Team familiarity | High: all shell code is Python or HTML |

**Pros:** reuses the prototype unchanged. Opens no listening port for the engine. Every mitigation is readable: strict CSP, `textContent` only, no remote URLs, downloads off, external links to the system browser, devtools off in release ([pywebview API](https://pywebview.flowrl.com/api/)).
**Cons:** no bundler, capability system or updater. Its security guide is two paragraphs.

### Option B: Tauri 2 with a Python sidecar
| Dimension | Assessment |
|-----------|------------|
| Complexity | High: Rust, capability JSON and a JS bridge |
| Cost | Smaller shell, which matters little next to a 32 MB to 400 MB model |
| Scalability | Single user, not a scale question |
| Team familiarity | Low: none of it is Python |

**Pros:** better installers, capabilities and an updater ([Tauri sidecar](https://v2.tauri.app/develop/sidecar/)).
**Cons:** unreviewable by the developer. Same system webviews, so no rendering gain. Its docs carry a "Linux Graphics Issues" page and there is an open blank-window report ([issue #15050](https://github.com/tauri-apps/tauri/issues/15050)); pywebview shares this Linux weak point, because both use WebKitGTK, so it is not a reason to prefer either.

### Option C: Electron with a Python child
| Dimension | Assessment |
|-----------|------------|
| Complexity | High: a Node layer and its security checklist |
| Cost | About 106 MB on Windows, per the earlier report |
| Scalability | Single user, not a scale question |
| Team familiarity | Low |

**Pros:** one Chromium everywhere.
**Cons:** large, and not Python.

### Option D: Localhost HTTP or WebSocket engine server
| Dimension | Assessment |
|-----------|------------|
| Complexity | Med: random port, token, Host checks |
| Cost | No extra package |
| Scalability | Single user, not a scale question |
| Team familiarity | High |

**Pros:** familiar web tooling.
**Cons:** invites DNS-rebinding and cross-origin attacks ([GitHub Blog](https://github.blog/security/application-security/dns-rebinding-attacks-explained-the-lookup-is-coming-from-inside-the-house/)). One developer reported start-up synchronisation pain.

One-file PyInstaller builds are out: they unpack on every launch, measured at 35 s for a data-science app ([Runcell](https://www.runcell.dev/blog/pyinstaller-vs-nuitka-benchmark)). Nuitka standalone stays a later answer to antivirus false positives.

## Trade-off Analysis
The pywebview, Tauri, attack and WebView2 facts are verified. The choices are judgement. The 35 s benchmark is macOS only, with no Windows antivirus cost measured, and there is no data for a spaCy bundle. A second source claimed Nuitka starts far faster but gave no method. Signing eligibility is verified: Azure Artifact Signing takes individuals only in the US or Canada, and SignPath needs an OSI licence, which FSL is not. Signing does not remove SmartScreen warnings at once. Whether Smart App Control blocks unsigned apps outright is not verified.

CI runs Windows Server 2025, not a Windows 10 or 11 client ([GitHub runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)), so it cannot show the consumer SmartScreen experience. The VM covers that, but must be rebuilt every 90 days, and its licence terms were not read in full.

Two points stay open. The prototype keeps theme and text size in browser storage, which `file://` may forget. pywebview's built-in server on 127.0.0.1 with a per-session token solves that but adds a port; whether the GTK bridge still uses an internal HTTP server in 6.x is unverified. The CDP debugging port must be impossible to enable in release builds. Other gaps: no start-up, memory or screen-reader figures; pywebview's licence file was not opened; Windows Job Objects from Python, JSON-RPC libraries, WiX, MSIX and Linux formats were not researched; axe-core integration was not verified.

## Consequences
- Easier: the CLI and the desktop app share one engine and one protocol.
- Easier: every release is built, installed and driven on Windows by CI, without the developer owning a Windows machine. This is a plan, not yet tried. CI runs a server edition of Windows, so the install warning a home user sees still needs a manual look on a 90-day evaluation machine, which must be rebuilt every 90 days.
- Harder: the project writes its own update notice, installer script and security rules.
- Revisit if antivirus flags the PyInstaller build (try Nuitka), or if start-up on the evaluation VM feels slow to a first-time user.

## Action Items
1. [ ] Open pywebview's licence file and confirm it is BSD.
2. [ ] Check whether pywebview 6.x on GTK opens an internal HTTP server, and document any port bound to loopback.
3. [ ] Make the CDP port unreachable in release builds and add a test for it.
4. [ ] Measure start-up time and memory of a one-dir build with spaCy on Linux and the Windows VM.
5. [x] Change Spec 13's shell item (done 12 Nov 2026).
6. [ ] Update Spec 9's signing text, and add the shell folder that ADR 0004 promises.
7. [ ] Gaps the research left, to close before the shell stage: no report was found of one developer shipping pywebview on both systems; the Qt fallback is unmeasured; orphan protection is untested; Wine, hourly cloud Windows machines and NSIS were not researched.

## Amendment (12 Nov 2026): Linux package, how pages load, and two licence notes

The owner decided three open points on 12 Nov 2026.

1. **Linux package: a `.deb` on GitHub Releases, plus a plain `tar.gz` for Fedora.** The `.deb` names WebKitGTK and PyGObject as system dependencies, so the system installs them, and the user gets a menu entry and a clean uninstall. AppImage lost: it still needs the system's WebKitGTK, and its menu entry and uninstall are manual. Flathub does not fit now: it requires builds entirely from source, rejects projects with little history, and forbids AI-assisted manifests ([Flathub requirements](https://docs.flathub.org/docs/for-app-authors/requirements)). Evidence is low to medium. **Before the shell stage, a trial must show that a PyInstaller build runs against the system's WebKitGTK.** A stock Debian 13 desktop does not have the WebKitGTK bindings installed, which is what the `.deb` dependency fixes.
2. **Pages load straight from files, with no local server.** Start pywebview with an absolute path and `http_server=False`. No port is opened. pywebview's built-in server would need a fixed port (42001) to keep browser storage, and it has no token, Host check or Origin check. The cost: with pywebview's default `private_mode=True`, browser storage is off, so theme and text size are saved by Python through the `js_api` facade and applied before each page loads. The prototype keeps using browser storage; the shell replaces those two calls. Set `ALLOW_FILE_URLS` to False explicitly, because pywebview's docs and code disagree on its default. This closes the open point on serving pages. It was read from pywebview's source, not run, and nothing was checked on Windows.
3. **PyGObject is allowed on Linux, by name.** PyGObject (LGPL-2.1 or later) is the bridge that lets Python open a GTK window. pywebview cannot open a window on Linux without it or Qt. The owner allowed it on 12 Nov 2026 as a named exception to the MIT, BSD and Apache rule, like pikepdf. With a `.deb` it comes from the user's system. List it on the third-party licences page.

Also checked that day:

- **pywebview's licence is BSD 3-Clause** (version 6.2.1 of 15 Apr 2026). Its other required packages are MIT or PSF. Avoid its PyQt6 extra, which is GPL or commercial. This closes action item 1.
- **The bridge needs no web server.** The GTK and WebView2 `js_api` bridges use native message handlers. Re-check this at the pinned version.
- **pywebview cannot block navigation to outside addresses.** Use a strict content security policy in each page, no outside links in the pages, a test for both, and one `js_api` call that opens a link in the system browser after the Spec 4.3 warning.
- **Pin the Windows CI image to `windows-2025`**, not `windows-latest`, which moves between versions over weeks.
- **Inno Setup has its own licence**, not an OSI one. It is free to use and is a build tool, not shipped code, so the runtime licence rule does not apply. It is preinstalled on the `windows-2025` image.

## Amendment (13 Nov 2026): the trial builds ran on Linux and Windows

Both trials are done. The scripts are on the branch `spike/windows-checks` (Windows, pushed, never to be merged) and the local branch `spike/local-archive` (Linux, with the full results file `spikes/linux/keep/RESULTS.md`).

**Linux: a PyInstaller build does run against the system's WebKitGTK.** Tested on Debian 13 with pywebview 6.2.1, PyInstaller 6.22.3, PyGObject 3.50.0 and WebKitGTK 2.54.0. The app and both WebKit helper processes loaded the system's `libwebkit2gtk-4.1`, shown by the loader's own trace and by each process's memory map. It needs two things:

1. **Leave the whole GTK stack out of the bundle,** not only WebKitGTK: GTK, GLib, their plug-ins, type files and shared data. The bundle is then 16 MB. PyInstaller's defaults give 241 MB and mix bundled GTK libraries into the system's WebKit processes, which worked only because the build and the run were on the same machine.
2. **Undo PyInstaller's environment before the window code loads.** PyInstaller points about ten GTK variables and `LD_LIBRARY_PATH` into the bundle, and the WebKit helpers inherit them. The app must reset them in its own first lines; a PyInstaller runtime hook runs too early.

A trial `.deb` of 7 MB was built, unpacked and run. Its dependency line, with each entry checked against what the bundled files need:

`libc6 (>= 2.38), libwebkit2gtk-4.1-0, gir1.2-webkit2-4.1, gir1.2-gtk-3.0, libgirepository-1.0-1, libglib2.0-0t64, libcairo2, libcairo-gobject2, libffi8, libssl3t64, libbz2-1.0, liblzma5, zlib1g, libexpat1, libuuid1`

`gir1.2-webkit2-4.1` is required: without it the app refused to start. The bundle needs glibc 2.38 or newer, which comes from the build machine's Python. So **release builds must be made on the oldest system the app supports** (Ubuntu 24.04 has 2.39, Debian 13 has 2.41; Ubuntu 22.04 and Mint 21, at 2.35, would need an older build machine).

**Windows: everything passed** on GitHub's Windows Server 2025 and 2022 runners, both run from source and frozen with PyInstaller: pages load from files, the Python bridge works, a link to a second page works and preferences survive it, no listening socket is opened, and another local file can't be read.

**What both systems showed, and the app must now do:**

| Finding | Consequence |
| --- | --- |
| A plain link to an `https://` address loads **inside the app window**, on both systems. pywebview only sends `target="_blank"` links to the browser | The app needs its own guard that refuses any navigation away from its own files. This is a security requirement (Spec 8.4), with a test |
| A bare file path makes pywebview start a local web server, even with `http_server=False`. A `file://` address does not | Always pass a `file://` address. A test checks that no socket is listening |
| The Python bridge is injected with `eval`, so a page policy of `default-src 'self'` silently breaks it | The pages' policy is `default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'`. This is weaker than hoped. It is acceptable because pages load only the app's own files and never show AI or contract text as HTML |
| With file access between files turned off, a page can't `fetch` even its own sibling files | Pages get all data through the Python bridge, as designed |
| `localStorage` does not exist on Linux in private mode, and does on Windows | Preferences stay in Python, as decided on 12 Nov |
| PyInstaller 6 puts data files in `_internal/` | Load pages from there, not from beside the program |

**Not tested:** installing the `.deb` with `dpkg` or apt; a real desktop session (the Linux runs used a virtual screen with no network); Wayland; Ubuntu, Mint and Fedora; a Windows installer; the navigation guard itself. Action items 1 and 2 of this record's trial are closed; these remain for the shell stage.

## Amendment (13 Nov 2026): real installs on Ubuntu, Fedora and Windows, with one still-open puzzle

The items left untested above were tried for real, on GitHub Actions runners, which have real root (unlike the developer's own machine). Scripts are on the local branches `spike/local-archive` (Linux) and `spike/windows-checks` (Windows, pushed, never to be merged).

**Ubuntu, real `apt`/`.deb` install: the install itself works.** `apt-get install -y ./clause-tracer-trial.deb` really resolved dependencies and installed, on both Ubuntu 22.04 and 24.04. The `Depends:` line from the first trial needed one change for 22.04: it predates the "t64" package-rename, so `libglib2.0-0t64` becomes `libglib2.0-0`, `libssl3t64` becomes `libssl3`, and the glibc floor drops from `2.38` to `2.35`. Everything else matched. The desktop file, a clean `apt-get remove`, and the file layout all checked out.

**Fedora, real `dnf` install: fully works, including running the app.** `python3-gobject`, `gtk3`, `webkit2gtk4.1` and `xorg-x11-server-Xvfb` installed by name, the tar.gz-style layout under `/opt` ran under Xvfb, and every check passed: the Python bridge, the link to a second page, no listening socket, the host's own WebKitGTK loaded (not a bundled copy).

**Windows: a real Inno Setup installer works end to end.** A silent install (`/VERYSILENT`), without admin rights (`PrivilegesRequired=lowest`, which the installer quietly redirects to the user's own profile instead of `Program Files`), a Start Menu shortcut, running the app from its installed location, and a silent uninstall that leaves nothing behind. Inno Setup 6 was already on GitHub's Windows runner; nothing extra had to be installed.

**Still open: the app's window never starts under GitHub's Ubuntu CI runners.** The install succeeds, but running the installed app under a virtual screen times out with `WebViewException: Main window failed to start`, on both Ubuntu versions. Two likely causes were tried and neither fixed it: WebKitGTK's own process sandbox (bubblewrap-based, which some CI images restrict) turned off, and software-only GL rendering forced. Fedora's container has no GPU either and starts the window fine, so the cause isn't simply "no GPU". This looks like something specific to GitHub's Ubuntu CI image rather than Ubuntu itself, but that isn't proven. It needs a real Ubuntu desktop or VM to settle, which the developer doesn't have.

**What this changes for the shell stage:** the `.deb`'s `Depends:` line needs the Ubuntu 22.04 variant above when that target is supported. The Windows installer can safely ask for no admin rights. The one open question — does the real app's window start on a real Ubuntu desktop — is the same trial script, just run somewhere with an actual screen; it is not a new unknown, only an unconfirmed one.
