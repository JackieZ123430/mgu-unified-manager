# Production desktop packaging

This repository now contains a reproducible installer pipeline for Windows
x64 and macOS (Apple Silicon and Intel). The installers bundle the GUI,
Python runtime, Tcl/Tk resources collected by PyInstaller, cryptography,
both vendor repositories, Node.js 22 and a standalone bundled ENET transport helper. Windows builds also bundle the
portable Win32-OpenSSH client. macOS uses the system OpenSSH client.

## Build outputs

- Windows: `MGU-Unified-Manager-Setup-Windows-x64.exe` (Inno Setup installer)
- macOS Apple Silicon: `MGU-Unified-Manager-macOS.dmg`
- macOS Intel: `MGU-Unified-Manager-macOS.dmg`

Each platform must be built on its matching runner. The macOS DMGs are
architecture-specific; they are not universal binaries.

## CI build

Push a tag such as `v1.0.0` or manually run the GitHub Actions workflow
`.github/workflows/build-installers.yml`. Download the generated artifacts
from the workflow run.

The workflow is a build pipeline, not a claim that binaries have already
been compiled or hardware-tested in this development environment.

## Local build inputs

PyInstaller spec expects the platform's Node.js 22 binary in `build_inputs/`.
On Windows it also expects portable Win32-OpenSSH files in
`build_inputs/openssh/`. The Windows prepare script downloads the latest
Win32-OpenSSH release. On macOS, system OpenSSH is used.

Windows:
1. Install Python 3.13 and Inno Setup 6.
2. Copy Node.js 22 `node.exe` to `build_inputs/node.exe`.
3. Run `packaging/prepare-windows.ps1`.
4. Install build dependencies with `python -m pip install -r packaging/requirements-build.txt`.
5. Build `mgu-connect.exe` using PyInstaller from `vendors/mgu-store/deploy/transport/mgu_connect.py`, with the transport folder on `--paths`, `--collect-all cryptography`, and hidden imports `hsfz` and `debug_cert`; place the result at `build_inputs/mgu-connect.exe`.
6. Build the desktop bundle with `pyinstaller packaging/mgu_unified_manager.spec --clean --noconfirm`.
7. Compile `packaging/windows/MGU-Unified-Manager.iss` with Inno Setup.

macOS:
1. Install Python 3.13 with Tcl/Tk support and Node.js 22.
2. Copy the matching `node` executable to `build_inputs/node`.
3. Run `packaging/prepare-macos.sh`.
4. Install build dependencies with `python3 -m pip install -r packaging/requirements-build.txt`.
5. Build the `mgu-connect` helper with PyInstaller from `vendors/mgu-store/deploy/transport/mgu_connect.py`, with the transport folder on `--paths`, `--collect-all cryptography`, and hidden imports `hsfz` and `debug_cert`; place it at `build_inputs/mgu-connect`.
6. Build the desktop bundle with `pyinstaller packaging/mgu_unified_manager.spec --clean --noconfirm`.
7. Run `packaging/macos/create-dmg.sh`.

## Runtime layout and user data

The copied MGU Store `deploy/hu` script uses the bundled transport helper instead of requiring a separate Python installation. Only the writable runtime copy is adapted; the original vendor source remains unchanged. The application copies vendor source files from its bundled resources into
the user's application-data directory on first launch. This writable copy
is required because SSH enrollment creates vehicle-specific private keys.
User data locations:
- Windows: `%LOCALAPPDATA%\\MGU Unified Manager`
- macOS: `~/Library/Application Support/MGU Unified Manager`

Logs, enrolled private keys and mutable state are stored outside the app
bundle so upgrades do not erase them. Do not include personal SSH keys,
tokens or enrollment files in release artifacts.

## OpenSSH and permissions

The Windows package includes portable Win32-OpenSSH. The app prepends its
directory to PATH so subprocesses from the upstream tools can find `ssh`.
On macOS, `/usr/bin/ssh` is used. ENET discovery and flashing may require
elevated permissions and a compatible network adapter; the installer does
not elevate the app automatically.

## Signing and notarization

The initial workflow creates unsigned installers. Public Windows releases
should be Authenticode-signed. Public macOS releases should be Developer ID
signed and notarized using Apple Developer credentials stored as GitHub
Actions secrets. Without signing/notarization, Windows SmartScreen and
macOS Gatekeeper may display warnings. Do not put signing certificates or
passwords in the repository.

## License and redistribution

The original vendor trees and license files are included. MGU Store is
GPL-3.0-or-later; distribute its corresponding source and required notices
in compliance with the GPL. The OpenSSH bundle carries its upstream license
files where supplied. Review all third-party notices before publishing.
