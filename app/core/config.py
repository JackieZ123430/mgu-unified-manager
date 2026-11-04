from pathlib import Path
import os
import shutil
import sys

APP_NAME = "MGU Unified Manager"

def resource_root() -> Path:
    # PyInstaller uses _MEIPASS; macOS app bundles can place resources under
    # Contents/Resources or Contents/Frameworks depending on bundle layout.
    if getattr(sys, "frozen", False):
        candidates = []
        if hasattr(sys, "_MEIPASS"):
            candidates.append(Path(sys._MEIPASS))
        exe_dir = Path(sys.executable).resolve().parent
        candidates.extend([exe_dir, exe_dir.parent / "Resources",
                           exe_dir.parent / "Frameworks",
                           exe_dir.parent / "Resources" / "_internal"])
        for candidate in candidates:
            if (candidate / "vendors").is_dir():
                return candidate
        return candidates[0] if candidates else exe_dir
    return Path(__file__).resolve().parents[2]

def user_data_root() -> Path:
    override = os.environ.get("MGU_MANAGER_HOME")
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
        return base / "MGU Unified Manager"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "MGU Unified Manager"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "mgu-unified-manager"

RESOURCE_ROOT = resource_root()
USER_DATA_ROOT = user_data_root()
USER_DATA_ROOT.mkdir(parents=True, exist_ok=True)

def _install_vendor_copy(name: str) -> Path:
    source = RESOURCE_ROOT / "vendors" / name
    destination = USER_DATA_ROOT / "vendors" / name
    if not source.is_dir():
        # Source-tree development fallback.
        source = Path(__file__).resolve().parents[2] / "vendors" / name
    if not source.is_dir():
        raise FileNotFoundError(f"Bundled vendor repository is missing: {name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Copy bundled upstream files to a persistent writable location. This is needed
    # because SSH enrollment creates private keys and the vendor repository stores
    # mutable enrollment state beneath its data directory.
    if not destination.exists():
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns("enrollments"))
        (destination / "data" / "enrollments").mkdir(parents=True, exist_ok=True)
    else:
        # Refresh packaged source files without overwriting per-vehicle enrollment data.
        for item in source.iterdir():
            target = destination / item.name
            if item.name == "data":
                target.mkdir(parents=True, exist_ok=True)
                for data_item in item.iterdir():
                    data_target = target / data_item.name
                    if data_item.name == "enrollments":
                        data_target.mkdir(parents=True, exist_ok=True)
                    elif data_item.is_dir():
                        shutil.copytree(data_item, data_target, dirs_exist_ok=True)
                    else:
                        shutil.copy2(data_item, data_target)
            elif item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)
    return destination

def bundled_node() -> Path | None:
    suffix = ".exe" if sys.platform == "win32" else ""
    candidate = RESOURCE_ROOT / "runtime" / ("node" + suffix)
    return candidate if candidate.is_file() else None


def bundled_transport() -> Path | None:
    suffix = ".exe" if sys.platform == "win32" else ""
    candidate = RESOURCE_ROOT / "runtime" / ("mgu-connect" + suffix)
    return candidate if candidate.is_file() else None

def patch_store_transport_bridge(store_repo: Path):
    # Patch only the writable user-data copy. The bundled upstream source remains unchanged.
    hu = store_repo / "deploy" / "hu"
    if not hu.is_file():
        return
    source = hu.read_text(encoding="utf-8")
    original = "const child = cp.spawn('python3', args, { stdio: ['pipe', 'pipe', 'inherit'] });"
    replacement = ("const transportBin = process.env.MGU_TRANSPORT_BIN;\n"
        "    const child = transportBin\n"
        "        ? cp.spawn(transportBin, args.slice(2), { stdio: ['pipe', 'pipe', 'inherit'], windowsHide: true })\n"
        "        : cp.spawn('python3', args, { stdio: ['pipe', 'pipe', 'inherit'] });")
    if original in source:
        hu.write_text(source.replace(original, replacement), encoding="utf-8")

SSH_REPO = _install_vendor_copy("idrive7-8-ssh-root")
STORE_REPO = _install_vendor_copy("mgu-store")
patch_store_transport_bridge(STORE_REPO)
VENDORS = USER_DATA_ROOT / "vendors"
ROOT = USER_DATA_ROOT
SSH_ENTRY = SSH_REPO / "ssh_enable.py"
SSH_GUI_ASSETS = SSH_REPO / "data" / "assets"
STORE_INSTALLER = STORE_REPO / "deploy" / "mgu-install.js"
STORE_DEPLOY = STORE_REPO / "deploy" / "hu"

def bundled_ssh_dir() -> Path | None:
    if sys.platform == "win32":
        candidate = RESOURCE_ROOT / "runtime" / "openssh"
        if (candidate / "ssh.exe").is_file():
            return candidate
    return None

def configure_runtime_path():
    paths = []
    ssh_dir = bundled_ssh_dir()
    if ssh_dir:
        paths.append(str(ssh_dir))
    node = bundled_node()
    if node:
        paths.append(str(node.parent))
    if paths:
        os.environ["PATH"] = os.pathsep.join(paths + [os.environ.get("PATH", "")])

configure_runtime_path()

def find_executable(name):
    if name == "node":
        node = bundled_node()
        if node:
            return str(node)
    if name == "ssh":
        ssh_dir = bundled_ssh_dir()
        if ssh_dir:
            candidate = ssh_dir / "ssh.exe"
            if candidate.is_file():
                return str(candidate)
    from shutil import which
    return which(name)

def default_identity(vin=""):
    enroll = SSH_REPO / "data" / "enrollments"
    if vin:
        safe = "".join(c for c in vin.upper() if c.isalnum() or c in "-_.") or vin
        candidates = [enroll / safe / "id_rsa"]
        candidates += [enroll / safe / "id_rsa.pkcs1.pem",
                       enroll / safe / "id_rsa.pkcs8.pem"]
        for p in candidates:
            if p.is_file():
                return p
    if enroll.is_dir():
        keys = []
        for folder in enroll.iterdir():
            for filename in ("id_rsa", "id_rsa.pkcs1.pem", "id_rsa.pkcs8.pem"):
                p = folder / filename
                if p.is_file():
                    keys.append(p)
        if keys:
            return max(keys, key=lambda p: p.stat().st_mtime)
    return None
