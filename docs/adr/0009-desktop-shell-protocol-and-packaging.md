# ADR-0009: Wrap the engine in pywebview, talk over stdio, ship one-dir with Inno Setup

**Status:** Accepted (12 Nov 2026)
**Date:** 2026-11-11
**Deciders:** Project owner

## Context
[Spec 9](../spec.md) builds a command-line tool first, then wraps it as a desktop app with an installer for Linux and Windows. The Windows installer is built by GitHub Actions and tested in a Windows virtual machine. Spec 13 lists the desktop shell as open, framed as "Tauri or Electron". [ADR 0004](0004-code-layout.md) says the shell gets its own folder and ADR.

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

### Option A: pywebview, stdio child, PyInstaller one-dir, Inno Setup (recommended)
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
**Cons:** unreviewable by the developer. Same system webviews, so no rendering gain. A "Linux Graphics Issues" page and an open blank-window report ([issue #15050](https://github.com/tauri-apps/tauri/issues/15050)).

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
- Easier: Windows is proven on every release without a Windows machine.
- Harder: the project writes its own update notice, installer script and security rules.
- Revisit if antivirus flags the PyInstaller build (try Nuitka), or if start-up on the evaluation VM feels slow to a first-time user.

## Action Items
1. [ ] Open pywebview's licence file and confirm it is BSD.
2. [ ] Check whether pywebview 6.x on GTK opens an internal HTTP server, and document any port bound to loopback.
3. [ ] Make the CDP port unreachable in release builds and add a test for it.
4. [ ] Measure start-up time and memory of a one-dir build with spaCy on Linux and the Windows VM.
5. [ ] If accepted, change Spec 13's shell item and Spec 9's signing text, and add the shell folder that ADR 0004 promises.
