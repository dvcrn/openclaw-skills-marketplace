import requests
import re
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from pathlib import Path
import csv
import kbmap
import datetime

DEFAULT_CREDS = [
    ("admin", "openclaw"),
    ("admin", "admin"),
    ("root", "root"),
    ("admin", "123456")
]

VULNERABLE_VERSIONS = {
    "1.0.0": ["CVE-2021-41617"],
    "1.1.0": ["CVE-2021-41617"],
    "1.2.0": ["CVE-2025-26465"],
    "v2026.3.2": []
}

SENSITIVE_PATHS = [
    "/api/status",
    "/api/v1/status",
    "/status",
    "/api/config",
    "/api/v1/config",
    "/config",
    "/debug",
    "/metrics",
    "/health",
    "/.env",
]

SENSITIVE_KEYWORDS_RE = re.compile(r"(token|api[_-]?key|secret|authorization|bearer|password|private[_-]?key)", re.IGNORECASE)

def _sev_rank(x):
    s = (x or "").strip().lower()
    if s == "critical":
        return 50
    if s == "high":
        return 40
    if s == "medium":
        return 30
    if s == "low":
        return 20
    if s == "info":
        return 10
    return 0

def _parse_version_nums(v):
    if not v or not isinstance(v, str):
        return None
    s = v.strip()
    if not s:
        return None
    s = s.lstrip("vV")
    parts = s.split(".")
    nums = []
    for p in parts:
        if not p.isdigit():
            return None
        nums.append(int(p))
    return tuple(nums) if nums else None

def _cmp_versions(a, b):
    va = _parse_version_nums(a)
    vb = _parse_version_nums(b)
    if va is None or vb is None:
        return None
    n = max(len(va), len(vb))
    va = va + (0,) * (n - len(va))
    vb = vb + (0,) * (n - len(vb))
    if va < vb:
        return -1
    if va > vb:
        return 1
    return 0

def _load_csv_cve_watchlist():
    cves = []
    try:
        base = Path(__file__).resolve().parent.parent
        csv_path = base / "papar" / "cve_analysis_result.csv"
        if not csv_path.exists():
            return cves
        with csv_path.open("r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                return cves
            header = [h.strip().lower() for h in rows[0]] if rows and rows[0] else []
            cve_col = 0
            if header and "cve" in header:
                cve_col = header.index("cve")
                data_rows = rows[1:]
            else:
                data_rows = rows
            for r in data_rows:
                if not r:
                    continue
                try:
                    v = r[cve_col].strip()
                except Exception:
                    continue
                if v and v.upper().startswith("CVE-"):
                    cves.append(v.upper())
    except Exception:
        return []
    return sorted({x for x in cves})

CSV_CVE_WATCHLIST = _load_csv_cve_watchlist()

def _is_https(url):
    return url.lower().startswith("https://")

def check_weak_credentials(url, timeout_s=2, verify=True):
    if not verify:
        warnings.simplefilter("ignore", InsecureRequestWarning)
    login_url = f"{url}/login"
    with requests.Session() as session:
        session.trust_env = False
        for username, password in DEFAULT_CREDS:
            try:
                response = session.post(
                    login_url,
                    json={"username": username, "password": password},
                    headers={"Content-Type": "application/json"},
                    timeout=timeout_s,
                    verify=verify,
                    allow_redirects=False,
                )
                if response.status_code == 200 and ("token" in response.text or "success" in response.text):
                    return {"vulnerable": True, "creds": f"{username}:{password}"}
            except requests.RequestException:
                continue
            
    return {"vulnerable": False}

def analyze_version(version):
    issues = []
    if version == "unknown":
        issues.append({
            "type": "unknown_version",
            "details": "Version could not be determined, manual verification recommended",
            "severity": "Low"
        })
    elif version in VULNERABLE_VERSIONS:
        cves = VULNERABLE_VERSIONS[version]
        if cves:
            issues.append({
                "type": "outdated_version",
                "version": version,
                "cves": cves,
                "severity": "High"
            })
    return issues

def check_sensitive_exposure(url, timeout_s=2, verify=True, max_bytes=65536):
    if not verify:
        warnings.simplefilter("ignore", InsecureRequestWarning)
    hits = []
    with requests.Session() as session:
        session.trust_env = False
        for p in SENSITIVE_PATHS:
            try:
                r = session.get(url + p, timeout=timeout_s, verify=verify, allow_redirects=False, stream=True)
            except requests.RequestException:
                continue
            if not r.ok:
                r.close()
                continue
            content_type = (r.headers.get("Content-Type") or "").lower()
            if "text" not in content_type and "json" not in content_type and "html" not in content_type:
                r.close()
                continue
            try:
                buf = bytearray()
                for chunk in r.iter_content(chunk_size=4096):
                    if not chunk:
                        break
                    remain = max_bytes - len(buf)
                    if remain <= 0:
                        break
                    if len(chunk) > remain:
                        buf.extend(chunk[:remain])
                        break
                    buf.extend(chunk)
                enc = r.encoding or "utf-8"
                text = bytes(buf).decode(enc, errors="ignore")
            finally:
                r.close()
            kws = {m.group(1).lower().replace("-", "_") for m in SENSITIVE_KEYWORDS_RE.finditer(text)}
            if kws:
                hits.append({"path": p, "keywords": sorted(kws)})
    if not hits:
        return None
    return {
        "type": "potential_sensitive_exposure",
        "details": "Sensitive keywords detected on unauthenticated endpoints",
        "severity": "Medium",
        "hits": hits,
    }

def run_analysis(service_info, assume_version=None, enable_cred_check=True, enable_exposure_check=True, timeout_s=2):
    url = service_info['url']
    print(f"[*] Analyzing service at {url}...")
    
    version = service_info.get("version")
    if assume_version and (not version or version == "unknown"):
        version = assume_version
    
    verify = True
    if _is_https(url):
        verify = bool(service_info.get("tls_verify", True))

    findings = {
        "target": url,
        "service": service_info.get("service"),
        "version": version,
        "port": service_info.get("port"),
        "scheme": service_info.get("scheme"),
        "evidence": service_info.get("evidence"),
        "tls_verify": verify if _is_https(url) else None,
        "vulnerabilities": []
    }
    
    version_issues = analyze_version(version)
    if version_issues:
        findings["vulnerabilities"].extend(version_issues)
        for issue in version_issues:
            print(f"[!] Vulnerability Found: {issue['type']} (CVEs: {issue.get('cves', [])})")
    
    if CSV_CVE_WATCHLIST:
        findings["csv_cve_watchlist"] = CSV_CVE_WATCHLIST
        top = CSV_CVE_WATCHLIST[:20]
        findings["vulnerabilities"].append({
            "type": "cve_watchlist",
            "details": f"{len(CSV_CVE_WATCHLIST)} CVEs loaded from papar/cve_analysis_result.csv",
            "cves": top,
            "severity": "Low"
        })
            
    if enable_cred_check:
        print("[*] Checking for weak credentials...")
        cred_check = check_weak_credentials(url, timeout_s=timeout_s, verify=verify)
        if cred_check['vulnerable']:
            vuln = {
                "type": "weak_credentials",
                "details": "Default credentials accepted (credentials redacted)",
                "severity": "Critical"
            }
            findings["vulnerabilities"].append(vuln)
            print("[!!!] CRITICAL: Weak Credentials Found!")
        else:
            print("[+] Credential check passed (no default credentials found)")

    if enable_exposure_check:
        exposure = check_sensitive_exposure(url, timeout_s=timeout_s, verify=verify)
        if exposure:
            findings["vulnerabilities"].append(exposure)

    findings["vulnerabilities"].sort(key=lambda v: (-_sev_rank(v.get("severity")), str(v.get("type") or "")))
    return findings

def analyze_audit_data(audit_data):
    """Analyze local audit data for OS and Node.js vulnerabilities."""
    vulns = []
    
    # 1. OS Analysis
    os_info = audit_data.get("os", {})
    patches = os_info.get("patches", [])
    
    if os_info.get("system") == "Windows":
        product = os_info.get("windows_product_name") or f"Windows {os_info.get('release')}"
        dv = os_info.get("windows_display_version") or os_info.get("windows_version")
        build = os_info.get("windows_build")
        parts = [str(product).strip()]
        if dv:
            parts.append(str(dv).strip())
        if build:
            parts.append(f"build {str(build).strip()}")
        vulns.append({
            "type": "windows_version",
            "details": " ".join([p for p in parts if p]),
            "severity": "Info",
        })

        latest_patch = os_info.get("latest_patch") if isinstance(os_info, dict) else None
        last_date_s = latest_patch.get("installed_on") if isinstance(latest_patch, dict) else None
        last_kb = latest_patch.get("hotfix") if isinstance(latest_patch, dict) else None
        last_dt = None
        if last_date_s:
            try:
                last_dt = datetime.date.fromisoformat(str(last_date_s))
            except Exception:
                last_dt = None

        if last_dt:
            label = f"{last_dt.isoformat()}" + (f" ({last_kb})" if last_kb else "")
            vulns.append({
                "type": "windows_last_security_update",
                "details": f"Last Security Update: {label}",
                "severity": "Info",
            })
            days = (datetime.date.today() - last_dt).days
            if days > 90:
                vulns.append({
                    "type": "windows_patch_lag",
                    "details": f"Patch is {days} days old (> 90 days): Update recommended",
                    "severity": "Medium",
                })
            else:
                vulns.append({
                    "type": "windows_patch_lag",
                    "details": f"Patch is {days} days old (<= 90 days): Up-to-date",
                    "severity": "Info",
                })
        else:
            vulns.append({
                "type": "windows_last_security_update",
                "details": "Last Security Update: Unknown (cannot determine hotfix install date)",
                "severity": "Medium",
            })

        dv_norm = str(dv).strip() if dv else None
        support = {"status": "Unknown", "end_date": None}
        is_win10 = False
        try:
            if product and "windows 10" in str(product).lower():
                is_win10 = True
            if is_win10 and dv_norm and dv_norm.lower() == "22h2":
                support["end_date"] = datetime.date(2025, 10, 14)
        except Exception:
            pass
        if support["end_date"]:
            if datetime.date.today() > support["end_date"]:
                support["status"] = "Out of support"
                sev = "High"
            else:
                support["status"] = "Supported"
                sev = "Info"
            vulns.append({
                "type": "windows_support_status",
                "details": f"Support status: {support['status']} (ends {support['end_date'].isoformat()})",
                "severity": sev,
            })
        else:
            vulns.append({
                "type": "windows_support_status",
                "details": "Support status: Unknown (lifecycle data not bundled)",
                "severity": "Info",
            })

        if is_win10:
            vulns.append({
                "type": "windows_upgrade_guidance",
                "details": "ZH: 检测到 Windows 10。建议评估升级到 Windows 11；若硬件/业务限制无法升级，请考虑注册 Windows 10 扩展安全更新（ESU）计划，以持续获取安全更新至 2026-10。 EN: Windows 10 detected. Consider upgrading to Windows 11; if not eligible, enroll in Windows 10 Extended Security Updates (ESU) to continue receiving security updates until 2026-10.",
                "severity": "Info",
            })

        cves_to_check = None
        if isinstance(audit_data, dict):
            pol = audit_data.get("policy", {})
            if isinstance(pol, dict) and isinstance(pol.get("windows_cves"), list):
                cves_to_check = pol.get("windows_cves")
        if cves_to_check:
            base = Path(__file__).resolve().parent.parent
            kb_map_path = base / "papar" / "windows_cve_kb_map.csv"
            if isinstance(audit_data, dict):
                pol = audit_data.get("policy", {})
                if isinstance(pol, dict) and pol.get("windows_kb_map_path"):
                    kb_map_path = Path(str(pol.get("windows_kb_map_path")))
            cve_kb_map = kbmap.load_cve_kb_map_csv(kb_map_path)
            if cve_kb_map:
                vulns.append({
                    "type": "windows_cve_check_scope",
                    "details": f"Checking KB installation for {len(cves_to_check)} CVEs",
                    "severity": "Info",
                })
                vulns.extend(kbmap.evaluate_missing_kbs(patches, cve_kb_map, cves=cves_to_check, include_unmapped=True))
            else:
                vulns.append({
                    "type": "windows_kb_map_missing",
                    "details": "CVE↔KB mapping file not found or empty; cannot assess CVE patch status",
                    "severity": "Low",
                })

    # 2. Node.js Analysis
    node_info = audit_data.get("node", {})
    version = node_info.get("version")
    
    if version:
        # Remove 'v' prefix
        v_clean = version.lstrip('v')
        
        # Simple version check logic (example)
        # Node < 18 is EOL
        try:
            major = int(v_clean.split('.')[0])
            if major < 18:
                vulns.append({
                    "type": "nodejs_eol",
                    "details": f"Node.js version {version} is End-of-Life (EOL)",
                    "severity": "Critical",
                    "cves": ["CVE-2023-32002", "CVE-2023-32559"] # Example EOL vulnerabilities
                })
            elif major == 18 and int(v_clean.split('.')[1]) < 19:
                 vulns.append({
                    "type": "nodejs_outdated",
                    "details": f"Node.js version {version} is outdated",
                    "severity": "Medium"
                })
        except:
            pass
            
        vulns.append({
            "type": "nodejs_info",
            "details": f"Node.js {version} (npm {node_info.get('npm_version')})",
            "severity": "Info"
        })
    else:
        vulns.append({
            "type": "nodejs_missing",
            "details": "Node.js not found in environment",
            "severity": "Low"
        })

    openclaw_info = audit_data.get("openclaw", {}) if isinstance(audit_data, dict) else {}
    latest = None
    if isinstance(audit_data, dict):
        pol = audit_data.get("policy", {})
        if isinstance(pol, dict):
            latest = pol.get("latest_openclaw_version")
    current = openclaw_info.get("version") if isinstance(openclaw_info, dict) else None
    openclaw_path = openclaw_info.get("path") if isinstance(openclaw_info, dict) else None

    if current:
        vulns.append({
            "type": "openclaw_cli_info",
            "details": f"OpenClaw CLI {current}",
            "severity": "Info"
        })
        if latest:
            cmp_res = _cmp_versions(current, latest)
            if cmp_res == -1:
                vulns.append({
                    "type": "openclaw_outdated",
                    "details": f"OpenClaw CLI version {current} is behind latest {latest}. ZH: 升级后部分或全部功能可能不可用，请谨慎判断。 EN: After upgrading, some or all functions may be unavailable; assess carefully.",
                    "severity": "High"
                })
            elif cmp_res is None and str(current).strip() != str(latest).strip():
                vulns.append({
                    "type": "openclaw_version_mismatch",
                    "details": f"OpenClaw CLI version {current} differs from latest {latest}. ZH: 升级后部分或全部功能可能不可用，请谨慎判断。 EN: After upgrading, some or all functions may be unavailable; assess carefully.",
                    "severity": "High"
                })
    elif openclaw_path:
        vulns.append({
            "type": "openclaw_cli_unreadable",
            "details": "OpenClaw CLI found but version unreadable from openclaw --version",
            "severity": "Low"
        })
    else:
        vulns.append({
            "type": "openclaw_cli_missing",
            "details": "OpenClaw CLI not found in PATH",
            "severity": "Low"
        })

    vulns.sort(key=lambda v: (-_sev_rank(v.get("severity")), str(v.get("type") or "")))
    return vulns
