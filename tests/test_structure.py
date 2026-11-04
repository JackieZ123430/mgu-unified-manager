from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_vendor_repositories_present():
    assert (ROOT / "vendors/idrive7-8-ssh-root/ssh_enable.py").is_file()
    assert (ROOT / "vendors/idrive7-8-ssh-root/gui.py").is_file()
    assert (ROOT / "vendors/mgu-store/deploy/mgu-install.js").is_file()
    assert (ROOT / "vendors/mgu-store/deploy/hu").is_file()

def test_unified_entrypoint_present():
    assert (ROOT / "run.py").is_file()
    assert (ROOT / "app/main.py").is_file()
