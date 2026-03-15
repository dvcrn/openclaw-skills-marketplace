import subprocess
import sys
import platform
import shutil
import re
import json
import datetime

def run_cmd(cmd, shell=False):
    """Run a command and return stdout. Returns None if command fails."""
    try:
        if shell and sys.platform == "win32":
            # For Windows shell commands, use powershell to ensure consistent output encoding
            cmd = ["powershell", "-Command", cmd] if isinstance(cmd, str) else cmd
            
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='ignore',
            shell=shell if sys.platform != "win32" else False # Avoid shell=True on Windows with list args
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None

def get_os_info():
    """Get basic OS information."""
    info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "patches": [],
        "patches_detailed": [],
        "windows_version": None,
        "windows_display_version": None,
        "windows_product_name": None,
        "windows_build": None,
        "latest_patch": None,
    }
    
    if info["system"] == "Windows":
        reg_json = run_cmd(
            r"Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' | "
            r"Select-Object ProductName,DisplayVersion,ReleaseId,CurrentBuildNumber,UBR | ConvertTo-Json -Compress",
            shell=True,
        )
        if reg_json:
            try:
                d = json.loads(reg_json)
                if isinstance(d, dict):
                    info["windows_product_name"] = d.get("ProductName") or None
                    info["windows_display_version"] = d.get("DisplayVersion") or d.get("ReleaseId") or None
                    b = d.get("CurrentBuildNumber")
                    ubr = d.get("UBR")
                    if b:
                        info["windows_build"] = f"{b}.{ubr}" if ubr is not None else str(b)
            except Exception:
                pass

        wv = run_cmd("(Get-ComputerInfo).WindowsVersion", shell=True)
        if wv:
            info["windows_version"] = wv.strip()

        # Get installed hotfixes
        # wmic qfe list brief /format:csv
        out = run_cmd("wmic qfe list brief /format:csv")
        if out:
            lines = out.splitlines()
            if len(lines) > 1:
                # Skip header
                # Node,Caption,CSName,Description,FixComments,HotFixID,InstallDate,InstalledBy,InstalledOn,Name,ServicePackInEffect,Status
                # Usually we care about HotFixID
                headers = lines[0].split(',')
                try:
                    idx = headers.index('HotFixID')
                    idx_on = headers.index('InstalledOn') if 'InstalledOn' in headers else -1
                    for line in lines[1:]:
                        parts = line.split(',')
                        if len(parts) > idx:
                            hotfix = parts[idx].strip()
                            if hotfix:
                                info["patches"].append(hotfix)
                                installed_on = None
                                if idx_on >= 0 and len(parts) > idx_on:
                                    installed_on = parts[idx_on].strip() or None
                                info["patches_detailed"].append({"hotfix": hotfix, "installed_on": installed_on})
                except ValueError:
                    # Fallback parsing if format is weird
                    import re
                    patches = re.findall(r"(KB\d+)", out)
                    info["patches"] = sorted(list(set(patches)))
                    info["patches_detailed"] = [{"hotfix": x, "installed_on": None} for x in info["patches"]]

        def _parse_date(s):
            t = (s or "").strip()
            if not t:
                return None
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    return datetime.datetime.strptime(t, fmt).date()
                except Exception:
                    pass
            m = re.match(r"^\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*$", t)
            if m:
                try:
                    return datetime.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
                except Exception:
                    return None
            return None

        latest = None
        for p in info.get("patches_detailed") or []:
            if not isinstance(p, dict):
                continue
            d = _parse_date(p.get("installed_on"))
            if not d:
                continue
            if not latest or d > latest.get("date"):
                latest = {"hotfix": p.get("hotfix"), "date": d}
        if latest:
            info["latest_patch"] = {"hotfix": latest.get("hotfix"), "installed_on": latest["date"].isoformat()}
    
    return info

def get_node_info():
    """Get Node.js environment information."""
    info = {
        "version": None,
        "npm_version": None,
        "vulnerabilities": []
    }
    
    # Check node version
    node_v = run_cmd(["node", "-v"])
    if node_v:
        info["version"] = node_v.strip()
        
    # Check npm version
    # On Windows, npm is a batch file, so we need shell=True or use "npm.cmd"
    # Using string command with shell=True triggers the powershell wrapper in run_cmd for Windows
    npm_v = run_cmd("npm -v", shell=True)
    if npm_v:
        info["npm_version"] = npm_v.strip()
        
    return info

def get_openclaw_info():
    info = {"path": None, "version_raw": None, "version": None}
    p = shutil.which("openclaw")
    if p:
        info["path"] = p
        v = None
        if sys.platform == "win32" and p.lower().endswith((".cmd", ".bat")):
            v = run_cmd("openclaw --version", shell=True)
        else:
            v = run_cmd(["openclaw", "--version"])
        if v:
            info["version_raw"] = v.strip()
            m = re.search(r"(v?\d+(?:\.\d+){1,3})", v)
            if m:
                info["version"] = m.group(1)
    return info

def get_openclaw_latest_version_from_npm(package="openclaw"):
    pkg = (package or "").strip()
    if not pkg:
        return None
    v = run_cmd(f"npm view {pkg} version", shell=True)
    if not v:
        return None
    s = str(v).strip()
    if not s:
        return None
    m = re.search(r"(v?\d+(?:\.\d+){1,3})", s)
    return m.group(1) if m else s

def audit_local_system():
    """Perform a local audit of OS and Node.js environment."""
    print("[*] Auditing local system...")
    
    os_info = get_os_info()
    print(f"[+] OS: {os_info['system']} {os_info['release']} (Patches found: {len(os_info['patches'])})")
    
    node_info = get_node_info()
    if node_info['version']:
        print(f"[+] Node.js: {node_info['version']}")
    else:
        print("[-] Node.js not found or not in PATH")

    openclaw_info = get_openclaw_info()
    if openclaw_info.get("version"):
        print(f"[+] OpenClaw CLI: {openclaw_info['version']}")
    elif openclaw_info.get("path"):
        print(f"[+] OpenClaw CLI: found ({openclaw_info['path']})")
    else:
        print("[-] OpenClaw CLI not found or not in PATH")
        
    return {
        "os": os_info,
        "node": node_info,
        "openclaw": openclaw_info,
    }
