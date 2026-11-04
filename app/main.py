import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path

from app.core.config import ROOT, SSH_REPO, STORE_REPO, default_identity
from app.core.logger import configure
from app.core.orchestrator import Orchestrator

BG = "#f3f5f8"
NAVY = "#17365d"
BLUE = "#2167c5"
GREEN = "#188653"
RED = "#b43c3c"
AMBER = "#b97820"

class UnifiedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MGU Unified Manager | iDrive 7 / 8")
        self.root.geometry("1120x780")
        self.root.minsize(900, 650)
        self.root.configure(bg=BG)
        self.events = queue.Queue()
        self.worker = None
        self.busy = False
        self.logger = configure(ROOT)
        self.vin = tk.StringVar()
        self.arch = tk.StringVar(value="id7")
        self.gateway = tk.StringVar(value="auto")
        self.mgu_ip = tk.StringVar()
        self.identity = tk.StringVar()
        self.component_id = tk.StringVar()
        self.restore_name = tk.StringVar(value="stock")
        self.status_text = tk.StringVar(value="Ready")
        self.orchestrator = Orchestrator(self.log, self.logger)
        self._style()
        self._build()
        self._load_identity()
        self.refresh_health()
        self.root.after(100, self._drain)

    def _style(self):
        style = ttk.Style()
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground="#1f2937", font=("Segoe UI", 10))
        style.configure("Hint.TLabel", background=BG, foreground="#64748b", font=("Segoe UI", 9))
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 10), font=("Segoe UI", 10, "bold"))
        style.configure("TButton", padding=(10, 7), font=("Segoe UI", 9, "bold"))
        style.configure("Primary.TButton", background=BLUE, foreground="white")
        style.map("Primary.TButton", background=[("active", "#164f9e"), ("disabled", "#aab4c0")])
        style.configure("Green.TButton", background=GREEN, foreground="white")
        style.configure("Red.TButton", background=RED, foreground="white")
        style.configure("Amber.TButton", background=AMBER, foreground="white")
        style.configure("Card.TLabelframe", background=BG, padding=12)
        style.configure("Card.TLabelframe.Label", background=BG, foreground=NAVY, font=("Segoe UI", 10, "bold"))

    def _build(self):
        header = tk.Frame(self.root, bg=NAVY, height=72)
        header.pack(fill="x")
        tk.Label(header, text="MGU UNIFIED MANAGER", bg=NAVY, fg="white",
                 font=("Segoe UI Semibold", 19)).pack(side="left", padx=22, pady=16)
        tk.Label(header, text="BMW iDrive 7 / iDrive 8", bg=NAVY, fg="#c9d7eb",
                 font=("Segoe UI", 10)).pack(side="left", pady=22)
        self.status_label = tk.Label(header, textvariable=self.status_text,
                                     bg=NAVY, fg="#d9e7f8", font=("Segoe UI", 10))
        self.status_label.pack(side="right", padx=22)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=14, pady=12)
        self.dashboard = ttk.Frame(self.tabs, padding=16)
        self.ssh_tab = ttk.Frame(self.tabs, padding=16)
        self.store_tab = ttk.Frame(self.tabs, padding=16)
        self.settings_tab = ttk.Frame(self.tabs, padding=16)
        self.tabs.add(self.dashboard, text="Dashboard")
        self.tabs.add(self.ssh_tab, text="Vehicle & SSH")
        self.tabs.add(self.store_tab, text="MGU Store")
        self.tabs.add(self.settings_tab, text="Settings")
        self._build_dashboard()
        self._build_ssh()
        self._build_store()
        self._build_settings()

        log_frame = ttk.LabelFrame(self.root, text="Activity log", style="Card.TLabelframe")
        log_frame.pack(fill="both", expand=False, padx=14, pady=(0, 10))
        self.console = scrolledtext.ScrolledText(log_frame, height=9, wrap="word",
            font=("Consolas", 9), bg="#111827", fg="#dbe4f0",
            insertbackground="white", relief="flat")
        self.console.pack(fill="both", expand=True)
        self.console.configure(state="disabled")
        bottom = tk.Frame(self.root, bg="#e4e9f0")
        bottom.pack(fill="x")
        tk.Label(bottom, text="Original repositories are retained under vendors/ and invoked through adapters.",
                 bg="#e4e9f0", fg="#526174", font=("Segoe UI", 9)).pack(side="left", padx=14, pady=6)
        ttk.Button(bottom, text="Clear log", command=self.clear_log).pack(side="right", padx=10, pady=3)

    def _build_dashboard(self):
        ttk.Label(self.dashboard, text="System overview", font=("Segoe UI Semibold", 19)).pack(anchor="w")
        ttk.Label(self.dashboard, text="One desktop interface for SSH provisioning and MGU application deployment.",
                  style="Hint.TLabel").pack(anchor="w", pady=(2, 14))
        cards = ttk.Frame(self.dashboard)
        cards.pack(fill="x")
        self.health_vars = {}
        for i, (key, label) in enumerate([
            ("python", "Python runtime"), ("node", "Node.js runtime"),
            ("ssh_cli", "OpenSSH client"), ("ssh_repository", "SSH Root module"),
            ("store_repository", "MGU Store module")
        ]):
            card = ttk.LabelFrame(cards, text=label, style="Card.TLabelframe")
            card.grid(row=i//3, column=i%3, sticky="nsew", padx=5, pady=5)
            var = tk.StringVar(value="Checking…")
            self.health_vars[key] = var
            ttk.Label(card, textvariable=var, font=("Segoe UI Semibold", 11)).pack(anchor="w")
            cards.columnconfigure(i%3, weight=1)
        actions = ttk.LabelFrame(self.dashboard, text="Quick actions", style="Card.TLabelframe")
        actions.pack(fill="x", pady=12)
        ttk.Button(actions, text="Discover vehicle", command=self.discover, style="Primary.TButton").pack(side="left", padx=4)
        ttk.Button(actions, text="Check SSH status", command=self.ssh_status).pack(side="left", padx=4)
        ttk.Button(actions, text="Install MGU Store", command=self.install_store, style="Green.TButton").pack(side="left", padx=4)
        ttk.Button(actions, text="Refresh health", command=self.refresh_health).pack(side="left", padx=4)
        note = ttk.LabelFrame(self.dashboard, text="Safety", style="Card.TLabelframe")
        note.pack(fill="x")
        ttk.Label(note, text=("Flashing can erase head-unit coding / CAFD definitions and BMW Digital Key pairings. "
                              "The manager never flashes automatically. Back up coding and confirm stable vehicle power "
                              "before any flash operation."), wraplength=1000, justify="left").pack(anchor="w")

    def _build_vehicle_fields(self, parent):
        row = ttk.Frame(parent); row.pack(fill="x", pady=5)
        ttk.Label(row, text="VIN").pack(side="left")
        ttk.Entry(row, textvariable=self.vin, width=24).pack(side="left", padx=8)
        ttk.Button(row, text="Detect VIN / gateway", command=self.discover).pack(side="left")
        ttk.Label(row, text="Variant").pack(side="left", padx=(18, 5))
        ttk.Combobox(row, textvariable=self.arch, values=["id7", "id8-bdc3", "id8-bcp"],
                     state="readonly", width=14).pack(side="left")
        ttk.Label(row, text="Gateway").pack(side="left", padx=(18, 5))
        ttk.Entry(row, textvariable=self.gateway, width=14).pack(side="left")
        ttk.Label(row, text="MGU IP").pack(side="left", padx=(18, 5))
        ttk.Entry(row, textvariable=self.mgu_ip, width=16).pack(side="left")

    def _build_ssh(self):
        ttk.Label(self.ssh_tab, text="Vehicle discovery & root SSH", font=("Segoe UI Semibold", 18)).pack(anchor="w")
        ttk.Label(self.ssh_tab, text="Uses the original idrive7-8-ssh-root implementation without editing its source.",
                  style="Hint.TLabel").pack(anchor="w", pady=(2, 10))
        self._build_vehicle_fields(self.ssh_tab)
        group = ttk.LabelFrame(self.ssh_tab, text="SSH operations", style="Card.TLabelframe")
        group.pack(fill="x", pady=10)
        ttk.Button(group, text="Read status (read-only)", command=self.ssh_status).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(group, text="Enable / repair (no flash)", command=self.ssh_enable, style="Green.TButton").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(group, text="Flash + enable", command=self.ssh_flash, style="Amber.TButton").grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(group, text="Fix refusing SSH key", command=self.ssh_fix, style="Amber.TButton").grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(group, text="Disable SSH", command=self.ssh_disable, style="Red.TButton").grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(group, text="Open vendor README", command=lambda: self.open_path(SSH_REPO / "README.md")).grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        for c in range(3): group.columnconfigure(c, weight=1)
        opts = ttk.Frame(self.ssh_tab); opts.pack(fill="x")
        self.persist = tk.BooleanVar(value=True)
        self.unique = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts, text="Persist SSH and turn debug mode off (recommended)",
                        variable=self.persist).pack(anchor="w")
        ttk.Checkbutton(opts, text="Generate unique per-vehicle SSH key (advanced; not recommended)",
                        variable=self.unique).pack(anchor="w")
        ttk.Label(self.ssh_tab, text="A flash is a destructive programming operation. The flash and fix-key actions require explicit confirmation.",
                  style="Hint.TLabel", wraplength=1000).pack(anchor="w", pady=8)

    def _build_store(self):
        ttk.Label(self.store_tab, text="MGU Store & application deployment", font=("Segoe UI Semibold", 18)).pack(anchor="w")
        ttk.Label(self.store_tab, text="Uses the original Node.js installer and deployment CLI. Node.js 18+ and root SSH access are required.",
                  style="Hint.TLabel").pack(anchor="w", pady=(2, 10))
        ttk.Label(self.store_tab, text="SSH identity shared with Vehicle & SSH:").pack(anchor="w")
        identity_row = ttk.Frame(self.store_tab); identity_row.pack(fill="x", pady=5)
        ttk.Entry(identity_row, textvariable=self.identity).pack(side="left", fill="x", expand=True)
        ttk.Button(identity_row, text="Browse…", command=self.choose_identity).pack(side="left", padx=6)
        install = ttk.LabelFrame(self.store_tab, text="Store bootstrap", style="Card.TLabelframe")
        install.pack(fill="x", pady=8)
        ttk.Button(install, text="Install / repair MGU Store", command=self.install_store,
                   style="Green.TButton").pack(side="left", padx=5)
        ttk.Button(install, text="Check installed components", command=self.store_status).pack(side="left", padx=5)
        ttk.Button(install, text="List backups", command=self.store_backups).pack(side="left", padx=5)
        manage = ttk.LabelFrame(self.store_tab, text="Component maintenance", style="Card.TLabelframe")
        manage.pack(fill="x", pady=8)
        ttk.Label(manage, text="Component ID").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(manage, textvariable=self.component_id, width=28).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(manage, text="Rollback component", command=self.store_rollback).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(manage, text="Uninstall component", command=self.store_uninstall, style="Red.TButton").grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(manage, text="Backup name (default: stock)").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(manage, textvariable=self.restore_name, width=28).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(manage, text="Restore backup", command=self.store_restore, style="Amber.TButton").grid(row=1, column=2, padx=5, pady=5)
        for c in range(4): manage.columnconfigure(c, weight=1)
        ttk.Label(self.store_tab, text=("App browsing, app installation and app updates are provided by the MGU Store UI on the head unit. "
                                        "This desktop panel bootstraps the Store and exposes the upstream deploy tool's component maintenance commands."),
                  style="Hint.TLabel", wraplength=1000, justify="left").pack(anchor="w", pady=8)

    def _build_settings(self):
        ttk.Label(self.settings_tab, text="Unified settings", font=("Segoe UI Semibold", 18)).pack(anchor="w")
        ttk.Label(self.settings_tab, text="The original repositories remain under vendors/. Settings here select the shared SSH key and show dependency state.",
                  style="Hint.TLabel").pack(anchor="w", pady=(2, 12))
        ttk.Label(self.settings_tab, text="Root SSH private key").pack(anchor="w")
        row = ttk.Frame(self.settings_tab); row.pack(fill="x", pady=5)
        ttk.Entry(row, textvariable=self.identity).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse…", command=self.choose_identity).pack(side="left", padx=6)
        ttk.Button(row, text="Auto-detect key for VIN", command=self._load_identity).pack(side="left")
        ttk.Label(self.settings_tab, text=f"SSH repository: {SSH_REPO}", style="Hint.TLabel", wraplength=1000).pack(anchor="w", pady=4)
        ttk.Label(self.settings_tab, text=f"MGU Store repository: {STORE_REPO}", style="Hint.TLabel", wraplength=1000).pack(anchor="w", pady=4)
        ttk.Button(self.settings_tab, text="Refresh dependency checks", command=self.refresh_health).pack(anchor="w", pady=10)

    def log(self, text):
        self.events.put(str(text))

    def _drain(self):
        try:
            while True:
                line = self.events.get_nowait()
                self.console.configure(state="normal")
                self.console.insert("end", line + "\n")
                self.console.see("end")
                self.console.configure(state="disabled")
        except queue.Empty:
            pass
        self.root.after(100, self._drain)

    def clear_log(self):
        self.console.configure(state="normal"); self.console.delete("1.0", "end"); self.console.configure(state="disabled")

    def _start(self, label, fn):
        if self.busy: return
        self.busy = True
        self.status_text.set(f"Running: {label}")
        self.log(f"\n=== {label} ===")
        def work():
            try:
                rc = fn()
                self.log(f"[{label} completed; exit code {rc}]")
            except Exception as exc:
                self.logger.exception("%s failed", label)
                self.log(f"ERROR: {exc}")
                rc = 1
            self.root.after(0, lambda: self._finish(label, rc))
        self.worker = threading.Thread(target=work, daemon=True)
        self.worker.start()

    def _finish(self, label, rc):
        self.busy = False
        self.status_text.set("Ready" if rc == 0 else f"{label}: failed ({rc})")
        if rc == 0:
            self.logger.info("%s completed successfully", label)
        else:
            self.logger.error("%s failed with exit code %s", label, rc)
        self._load_identity(silent=True)

    def _load_identity(self, silent=False):
        key = default_identity(self.vin.get())
        if key and not self.identity.get().strip():
            self.identity.set(str(key))
        elif key and self.vin.get().strip():
            self.identity.set(str(key))
        if not key and not silent:
            self.log("No saved SSH identity found yet. Provision SSH first, then select the generated key.")

    def choose_identity(self):
        path = filedialog.askopenfilename(title="Select root SSH private key",
            filetypes=[("SSH private keys", "*"), ("All files", "*.*")])
        if path: self.identity.set(path)

    def _ssh_args(self, action, persist=False):
        args = [action, "--yes", "--arch", self.arch.get(), "--gateway", self.gateway.get().strip() or "auto"]
        if self.vin.get().strip(): args += ["--vin", self.vin.get().strip()]
        if self.mgu_ip.get().strip(): args += ["--mgu-ip", self.mgu_ip.get().strip()]
        if persist:
            args.append("--persist")
            if not self.persist.get(): args.append("--keep-debug")
            args.append("--unique-key" if self.unique.get() else "--no-unique-key")
        return args

    def _run_ssh(self, action, persist=False):
        def fn():
            return self.orchestrator.ssh.run(self._ssh_args(action, persist))
        self._start(f"SSH {action}", fn)

    def ssh_status(self): self._run_ssh("status")
    def ssh_enable(self): self._run_ssh("enable", True)
    def ssh_disable(self):
        if messagebox.askyesno("Disable root SSH", "Revert persistence and stop SSH on the head unit?"):
            self._run_ssh("disable")
    def ssh_flash(self):
        if not self.vin.get().strip():
            messagebox.showerror("VIN required", "Enter a VIN or detect it before flashing.")
            return
        warning = ("FLASH WARNING\n\nFlashing can erase HU coding / CAFD definitions and BMW Digital Key pairings. "
                   "It can also brick the head unit. Back up coding first and ensure stable vehicle power.\n\n"
                   "This operation is never performed automatically.\n\nContinue with Flash + Enable?")
        if messagebox.askyesno("Destructive operation", warning):
            self._run_ssh("flash", True)
    def ssh_fix(self):
        if not self.vin.get().strip():
            messagebox.showerror("VIN required", "Enter a VIN or detect it before Fix-key.")
            return
        if messagebox.askyesno("Destructive repair", "Fix-key re-flashes the head unit. Coding and Digital Key warnings apply. Continue?"):
            self._run_ssh("fix-key", True)

    def discover(self):
        def fn():
            found = self.orchestrator.ssh.discover(self.log)
            if not found:
                self.log("No ENET gateway responded. Check cable, adapter and vehicle wake state.")
                return 1
            g = found[0]
            def apply():
                if getattr(g, "vin", None): self.vin.set(g.vin)
                if getattr(g, "ip", None): self.gateway.set(g.ip)
                self._load_identity(silent=True)
            self.root.after(0, apply)
            self.log(f"Discovered gateway {getattr(g, 'ip', 'unknown')}; VIN: {getattr(g, 'vin', None) or 'not reported'}")
            return 0
        self._start("Vehicle discovery", fn)

    def _store_key(self):
        key = self.identity.get().strip()
        if not key:
            self._load_identity(silent=True); key = self.identity.get().strip()
        return Path(key) if key else None

    def install_store(self):
        key = self._store_key()
        def fn():
            rc, _ = self.orchestrator.store.install_store(key)
            return rc
        self._start("Install MGU Store", fn)

    def _deploy(self, command, extra=()):
        key = self._store_key()
        def fn():
            rc, _ = self.orchestrator.store.deploy_command(command, key, extra)
            return rc
        self._start(f"MGU deploy: {command}", fn)

    def store_status(self): self._deploy("status", ["--json"])
    def store_backups(self): self._deploy("backups")
    def store_rollback(self):
        cid = self.component_id.get().strip()
        if not cid: messagebox.showerror("Component ID required", "Enter a component ID."); return
        if messagebox.askyesno("Rollback", f"Rollback component '{cid}' to its previous version?"):
            self._deploy("rollback", [cid, "--yes"])
    def store_uninstall(self):
        cid = self.component_id.get().strip()
        if not cid: messagebox.showerror("Component ID required", "Enter a component ID."); return
        if messagebox.askyesno("Uninstall component", f"Uninstall '{cid}' from the head unit?"):
            self._deploy("uninstall", [cid, "--yes"])
    def store_restore(self):
        name = self.restore_name.get().strip() or "stock"
        if messagebox.askyesno("Restore backup", f"Restore head-unit backup '{name}'? This changes installed components."):
            self._deploy("restore", [name, "--yes"])

    def refresh_health(self):
        info = self.orchestrator.health()
        for key, value in info.items():
            if key in self.health_vars:
                self.health_vars[key].set("Available" if value is True else "Missing" if value is False else str(value))
        self.log("Health check: " + "; ".join(f"{k}={v}" for k, v in info.items()))

    def open_path(self, path):
        import subprocess, sys
        path = str(path)
        if sys.platform == "win32": os.startfile(path)
        elif sys.platform == "darwin": subprocess.Popen(["open", path])
        else: subprocess.Popen(["xdg-open", path])

def main():
    root = tk.Tk()
    UnifiedGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
