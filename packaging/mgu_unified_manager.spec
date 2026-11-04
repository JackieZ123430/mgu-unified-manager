# Build with: pyinstaller packaging/mgu_unified_manager.spec --clean
from pathlib import Path
import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPECPATH).resolve().parent
INPUTS = ROOT / "build_inputs"
sys.path.insert(0, str(ROOT / "vendors" / "idrive7-8-ssh-root"))
NODE_NAME = "node.exe" if os.name == "nt" else "node"
NODE = INPUTS / NODE_NAME
TRANSPORT_NAME = "mgu-connect.exe" if os.name == "nt" else "mgu-connect"
TRANSPORT = INPUTS / TRANSPORT_NAME
if not NODE.is_file():
    raise SystemExit(f"Missing bundled Node runtime: {NODE}. Run the platform prepare script first.")
if not TRANSPORT.is_file():
    raise SystemExit(f"Missing bundled transport helper: {TRANSPORT}. Build it before the GUI.")

datas = [(str(ROOT / "vendors"), "vendors")]
binaries = [(str(NODE), "runtime"), (str(TRANSPORT), "runtime")]
if os.name == "nt":
    ssh_dir = INPUTS / "openssh"
    if not (ssh_dir / "ssh.exe").is_file():
        raise SystemExit("Missing portable OpenSSH in build_inputs/openssh")
    binaries += [(str(p), "runtime/openssh") for p in ssh_dir.iterdir() if p.is_file()]
binaries += [(str(p), "runtime") for p in INPUTS.glob("*.dll")]

crypt_data, crypt_bins, crypt_hidden = collect_all("cryptography")
datas += crypt_data
binaries += crypt_bins
hiddenimports = ["ssh_enable"] + crypt_hidden + collect_submodules("mgu7")

a = Analysis(
    [str(ROOT / "run.py")], pathex=[str(ROOT)],
    binaries=binaries, datas=datas, hiddenimports=hiddenimports,
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=["pytest", "unittest"], noarchive=False,
)
pyz = PYZ(a.pure)

if os.name == "nt":
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
              name="MGU Unified Manager", debug=False,
              bootloader_ignore_signals=False, strip=False, upx=False,
              console=False, disable_windowed_traceback=False)
    app = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,
                  upx_exclude=[], name="MGU Unified Manager")
else:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas,
              name="MGU Unified Manager", debug=False,
              bootloader_ignore_signals=False, strip=False, upx=False,
              console=False, disable_windowed_traceback=False)
    app = BUNDLE(exe, name="MGU Unified Manager.app", icon=None,
                 bundle_identifier="com.mguunified.manager",
                 info_plist={"NSHighResolutionCapable": "True",
                             "LSApplicationCategoryType": "public.app-category.utilities"})
