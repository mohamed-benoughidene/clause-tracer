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
