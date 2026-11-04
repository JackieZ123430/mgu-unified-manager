# MGU Unified Manager

A single Tkinter desktop application that coordinates the BMW MGU
iDrive 7/8 SSH-root and the MGU Store.


## Requirements

- Python 3.9 or newer.
- Tkinter (included with most standard Python distributions; Linux may need
  the OS package `python3-tk`).
- `cryptography>=41.0` for the SSH-root project.
- Node.js 18 or newer for MGU Store computer-side installer.
- OpenSSH client (`ssh`) on PATH.
- Windows 10/11, macOS or Linux.

## Run

```bash
python -m pip install -r requirements.txt
python run.py
```

Windows users can also run `run.bat`; macOS/Linux users can run `./run.sh`.

## First use

1. Connect the vehicle over ENET and wake the head unit.
2. Open **Vehicle & SSH** and select the correct MGU variant.
3. Use **Detect VIN / gateway** or enter the VIN manually.
4. If SSH is already provisioned, run **Read status** and locate the generated
   private key under `vendors/idrive7-8-ssh-root/data/enrollments/<VIN>/`.
5. If SSH is not provisioned, read the upstream SSH project's warnings and
   back up vehicle coding before explicitly choosing **Flash + enable**.
6. Select the generated private key in **Settings** or **MGU Store**.
7. Install/repair MGU Store. The installer checks packages and uses the
   original upstream deployment logic.

## Safety

**Flashing is not automatic.** Flash and fix-key require a separate GUI
confirmation. Flashing can erase HU coding / CAFD definitions, remove BMW
Digital Key pairings and, in the worst case, damage the head unit. Back up
coding and ensure stable vehicle power before proceeding. Never run a flash
merely to repair an SSH connection; use the non-flashing Enable operation
when appropriate.

Store installation and deployment change the head unit. Keep the vehicle
parked and on stable power. The GUI suppresses the installer's interactive
restart prompt; read its output and restart the head unit only when safe.

Private keys remain in the vendor enrollment directory or the user-selected
path. Do not commit private keys, asset certificates or tokens. The upstream
SSH project assets are not bundled if absent from the supplied archive; the
original project will report missing required assets rather than inventing them.

## Architecture

```text
Tkinter unified GUI
  └── Orchestrator
      ├── SSHRootAdapter -> original Python ssh_enable.main()
      ├── MGUStoreAdapter -> Node 18+ mgu-install.js / deploy/hu
      ├── ProcessRunner -> timeout, output streaming, exit codes
      └── shared identity path, logging and health checks

vendors/
  ├── idrive7-8-ssh-root/   # original repository, retained
  └── mgu-store/            # original repository, retained
```

The Python and Node runtimes remain isolated. The head unit's own Node 8
runtime is not upgraded by this wrapper.

## Tests

```bash
python -m pip install pytest
pytest
```

The included automated tests validate the wrapper layout only. Real ENET,
SSH provisioning and MGU deployment tests require compatible BMW hardware
and must be run separately.

## Licensing

The upstream repositories retain their original LICENSE files and notices.
The SSH-root repository is Unlicense; MGU Store is GPL-3.0-or-later and
includes `THIRD_PARTY_NOTICES.md`. Review GPL obligations before redistributing
a combined binary or installer. This wrapper does not relicense either vendor
project.

## Troubleshooting

- **Node missing / too old:** install Node.js 18+ and restart the GUI.
- **SSH key not found:** use Settings → Browse and choose the private key
  created by the SSH-root enrollment operation (`id_rsa` or PEM variant).
- **Store reports no SSH:** verify the identity belongs to this vehicle and
  that root SSH is already active.
- **No ENET gateway:** check the ENET cable, adapter link-local address and
  that the vehicle is awake.
- **Missing SSH flash assets:** the source archive may not contain the
  original project's `data/assets` payloads. Obtain them from the upstream
  project's authorized distribution; do not substitute arbitrary binaries.
