import argparse
import scanner
import analyzer
import audit
import kbmap
import msrc
import json
import sys
import os
from pathlib import Path
import subprocess
import re
import html as _html
from concurrent.futures import ThreadPoolExecutor, as_completed

def _h(x):
    return _html.escape("" if x is None else str(x), quote=True)

def main():
    parser = argparse.ArgumentParser(description="OpenClaw Vulnerability Scanner")
    parser.add_argument("target", nargs="?", help="IP address or hostname of the target")
    parser.add_argument("--targets-file", help="File containing targets, one per line", default=None)
    parser.add_argument("--port", type=int, help="Port to scan (optional, otherwise default ports)", default=None)
    parser.add_argument("--ports", help="Comma-separated ports to scan", default=None)
    parser.add_argument("--max-workers", type=int, default=64)
    parser.add_argument("--port-timeout", type=float, default=0.5)
    parser.add_argument("--http-timeout", type=float, default=2.0)
    parser.add_argument("--assume-version", default=None)
    parser.add_argument("--skip-cred-check", action="store_true")
    parser.add_argument("--skip-leak-check", action="store_true")
    parser.add_argument("--insecure", action="store_true", help="Allow insecure HTTPS (skip TLS certificate verification) for probing")
    parser.add_argument("--audit", action="store_true", help="Perform local OS/Node.js audit (requires local execution)")
    parser.add_argument("--latest-openclaw-version", default=None, help="Latest OpenClaw version string for local CLI comparison (e.g. v2026.3.2)")
    parser.add_argument("--npm-view-latest-openclaw", action="store_true", help="Fetch latest OpenClaw version from npm registry via `npm view openclaw version`")
    parser.add_argument("--kb-map-path", default=None, help="Path to Windows CVE↔KB mapping CSV (default: papar/windows_cve_kb_map.csv)")
    parser.add_argument("--windows-cves", default=None, help="Comma-separated CVEs to check against Windows KB mapping")
    parser.add_argument("--windows-cves-file", default=None, help="File containing CVEs (one per line) to check against Windows KB mapping")
    parser.add_argument("--msrc-cvrf-id", default=None, help="MSRC CVRF ID to fetch (e.g. 2026-Mar)")
    parser.add_argument("--msrc-cvrf-ids", default=None, help="Comma-separated MSRC CVRF IDs to fetch and merge (e.g. 2026-Jan,2026-Feb,2026-Mar)")
    parser.add_argument("--msrc-cvrf-from", default=None, help="Start MSRC CVRF ID (inclusive) for month range (e.g. 2016-Jan)")
    parser.add_argument("--msrc-cvrf-to", default=None, help="End MSRC CVRF ID (inclusive) for month range (e.g. 2026-Mar)")
    parser.add_argument("--msrc-cvrf-cache-dir", default=None, help="Directory to cache downloaded CVRF JSON (default: papar/msrc_cvrf_cache)")
    parser.add_argument("--msrc-cvrf-rate-limit", type=float, default=0.6, help="Seconds to wait between CVRF requests (default: 0.6)")
    parser.add_argument("--msrc-cvrf-retries", type=int, default=4, help="Retry count for CVRF requests (default: 4)")
    parser.add_argument("--merge-existing-kb-map", action="store_true", help="Merge with existing windows_cve_kb_map.csv instead of overwriting")
    parser.add_argument("--update-windows-kb-map", action="store_true", help="Fetch MSRC CVRF and generate/update local Windows CVE↔KB mapping CSV")
    parser.add_argument("--watchlist-path", default=None, help="Path to CVE watchlist CSV (default: papar/cve_analysis_result.csv)")
    parser.add_argument("--check-watchlist-all", action="store_true", help="Check all CVEs from watchlist CSV against Windows KB mapping")
    parser.add_argument("--msrc-api-key", default=None, help="MSRC SUG API key for CVE->KB lookup (optional; can also use env MSRC_API_KEY)")
    parser.add_argument("--update-windows-kb-map-from-watchlist", action="store_true", help="Use MSRC SUG API to map all watchlist CVEs to KBs and update mapping CSV")
    parser.add_argument("--out-dir", default="output")
    parser.add_argument("--no-html", action="store_true")
    args = parser.parse_args()

    # Allow running just audit without target
    if not args.target and not args.targets_file and not args.audit:
        parser.print_help()
        sys.exit(2)

    targets = []
    if args.target:
        targets.append(args.target.strip())
    if args.targets_file:
        p = Path(args.targets_file)
        if p.exists():
            for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                t = line.strip()
                if t and not t.startswith("#"):
                    targets.append(t)
    
    # If no targets but audit is requested, just do audit
    if not targets and args.audit:
        print("[*] No network targets provided, performing local audit only.")

    targets = [t for i, t in enumerate(targets) if t and t not in targets[:i]]
    
    def _validate_port(p):
        return isinstance(p, int) and 1 <= p <= 65535

    ports = None
    if args.ports:
        try:
            ports = [int(x.strip()) for x in args.ports.split(",") if x.strip()]
        except ValueError:
            parser.error("--ports must be a comma-separated list of integers")
        bad = [p for p in ports if not _validate_port(p)]
        if bad:
            parser.error(f"Invalid port(s) in --ports: {', '.join(str(x) for x in bad)} (valid range: 1-65535)")
    elif args.port:
        if not _validate_port(args.port):
            parser.error("--port must be in range 1-65535")
        ports = [args.port]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_base = "scan_report"
    run_id = "latest"

    def get_local_bindings(ports_to_check):
        if not ports_to_check:
            return {}
        if sys.platform != "win32":
            return {}
        try:
            out = subprocess.check_output(["netstat", "-ano", "-p", "tcp"], text=True, encoding="utf-8", errors="ignore")
        except Exception:
            return {}
        bindings = {int(p): [] for p in ports_to_check}
        pat = re.compile(r"^\s*TCP\s+(\S+):(\d+)\s+\S+\s+LISTENING\s+(\d+)\s*$", re.IGNORECASE)
        for line in out.splitlines():
            m = pat.match(line)
            if not m:
                continue
            addr, port_s, pid_s = m.group(1), m.group(2), m.group(3)
            try:
                port_i = int(port_s)
            except ValueError:
                continue
            if port_i not in bindings:
                continue
            bindings[port_i].append({"local_address": addr, "pid": int(pid_s)})
        return bindings
    
    local_audit_results = None
    if args.audit:
        try:
            raw_audit = audit.audit_local_system()
            raw_audit.setdefault("policy", {})
            if isinstance(raw_audit.get("policy"), dict):
                base = Path(__file__).resolve().parent.parent
                pol = raw_audit["policy"]

                kb_map_path = Path(args.kb_map_path) if args.kb_map_path else (base / "papar" / "windows_cve_kb_map.csv")
                pol["windows_kb_map_path"] = str(kb_map_path)
                watchlist_path = Path(args.watchlist_path) if args.watchlist_path else (base / "papar" / "cve_analysis_result.csv")
                pol["watchlist_path"] = str(watchlist_path)

                if args.windows_cves or args.windows_cves_file:
                    cves = []
                    if args.windows_cves:
                        cves.extend([x.strip() for x in str(args.windows_cves).split(",") if x.strip()])
                    if args.windows_cves_file:
                        p = Path(args.windows_cves_file)
                        if p.exists():
                            for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                                t = line.strip()
                                if t and not t.startswith("#"):
                                    cves.append(t)
                    cves = [x.upper() for x in cves]
                    cves = [x for i, x in enumerate(cves) if x and x not in cves[:i]]
                    if cves:
                        pol["windows_cves"] = cves
                elif args.check_watchlist_all:
                    pol["windows_cves"] = kbmap.load_cves_from_csv(watchlist_path)

                if args.update_windows_kb_map:
                    ids = []
                    if args.msrc_cvrf_id:
                        ids.append(str(args.msrc_cvrf_id).strip())
                    if args.msrc_cvrf_ids:
                        ids.extend([x.strip() for x in str(args.msrc_cvrf_ids).split(",") if x.strip()])
                    if args.msrc_cvrf_from or args.msrc_cvrf_to:
                        if not (args.msrc_cvrf_from and args.msrc_cvrf_to):
                            parser.error("--msrc-cvrf-from and --msrc-cvrf-to must be used together")
                        ids.extend(msrc.generate_cvrf_ids(args.msrc_cvrf_from, args.msrc_cvrf_to))
                    ids = [x for i, x in enumerate(ids) if x and x not in ids[:i]]
                    if not ids:
                        parser.error("--update-windows-kb-map requires --msrc-cvrf-id, --msrc-cvrf-ids, or --msrc-cvrf-from/--msrc-cvrf-to")

                    base_map = {}
                    if args.merge_existing_kb_map:
                        base_map = kbmap.load_cve_kb_map_csv(kb_map_path)

                    merged = {k: set(v) for k, v in (base_map or {}).items()}
                    cache_dir = Path(args.msrc_cvrf_cache_dir) if args.msrc_cvrf_cache_dir else (base / "papar" / "msrc_cvrf_cache")
                    cvrf_failed = []
                    for cid in ids:
                        try:
                            doc = msrc.fetch_cvrf_document_cached(
                                cid,
                                cache_dir=cache_dir,
                                timeout_s=15,
                                rate_limit_s=float(args.msrc_cvrf_rate_limit),
                                retries=int(args.msrc_cvrf_retries),
                            )
                        except Exception:
                            if len(cvrf_failed) < 50:
                                cvrf_failed.append(cid)
                            continue
                        mapping = kbmap.extract_cve_kb_map_from_cvrf(doc)
                        for cve, kbs in (mapping or {}).items():
                            merged.setdefault(cve, set()).update(set(kbs or set()))

                    source = "msrc_cvrf:" + ",".join(ids)
                    kbmap.save_cve_kb_map_csv(kb_map_path, merged, source=source)
                    pol["msrc_cvrf_ids"] = ids
                    pol["msrc_cvrf_cache_dir"] = str(cache_dir)
                    pol["msrc_cvrf_rate_limit"] = float(args.msrc_cvrf_rate_limit)
                    pol["windows_kb_map_count"] = len(merged)
                    if cvrf_failed:
                        pol["msrc_cvrf_failed_count"] = len(cvrf_failed)
                        pol["msrc_cvrf_failed_sample"] = cvrf_failed[:20]

                if args.update_windows_kb_map_from_watchlist:
                    key = (args.msrc_api_key or os.environ.get("MSRC_API_KEY") or "").strip()
                    if not key:
                        parser.error("--update-windows-kb-map-from-watchlist requires --msrc-api-key or env MSRC_API_KEY")
                    all_cves = kbmap.load_cves_from_csv(watchlist_path)
                    base_map = kbmap.load_cve_kb_map_csv(kb_map_path) if args.merge_existing_kb_map else {}
                    merged = {k: set(v) for k, v in (base_map or {}).items()}
                    updated = 0
                    missing = [c for c in all_cves if c and not (c in merged and merged.get(c))]
                    chunk = 25
                    for i in range(0, len(missing), chunk):
                        group = missing[i:i+chunk]
                        try:
                            m = msrc.fetch_kbs_by_cves_sug(group, key)
                        except Exception:
                            m = {}
                        for cve, kbs in (m or {}).items():
                            if kbs:
                                if not merged.get(cve):
                                    updated += 1
                                merged.setdefault(cve, set()).update(set(kbs))
                    kbmap.save_cve_kb_map_csv(kb_map_path, merged, source="msrc_sug")
                    pol["windows_kb_map_count"] = len(merged)
                    pol["windows_kb_map_updated_from_watchlist"] = updated

                if args.latest_openclaw_version:
                    pol["latest_openclaw_version"] = args.latest_openclaw_version
                elif args.npm_view_latest_openclaw:
                    latest = audit.get_openclaw_latest_version_from_npm()
                    if latest:
                        pol["latest_openclaw_version"] = latest
            local_audit_results = {
                "raw": raw_audit,
                "findings": analyzer.analyze_audit_data(raw_audit)
            }
        except Exception as e:
            print(f"[-] Local audit failed: {e}")

    print(f"[*] Starting OpenClaw Scan for {len(targets)} target(s)...")
    results = []

    def scan_one(t):
        scan_res = scanner.run_scan(
            t,
            ports=ports,
            port_timeout_s=args.port_timeout,
            http_timeout_s=args.http_timeout,
            max_workers=args.max_workers,
            insecure=args.insecure,
        )
        services = scan_res.get("services", [])
        findings = []
        for s in services:
            findings.append(
                analyzer.run_analysis(
                    s,
                    assume_version=args.assume_version,
                    enable_cred_check=not args.skip_cred_check,
                    enable_exposure_check=not args.skip_leak_check,
                    timeout_s=args.http_timeout,
                )
            )
        local_bindings = {}
        if t in ("127.0.0.1", "localhost", "::1"):
            local_bindings = get_local_bindings(scan_res.get("open_ports", []))
        return {
            "target": t,
            "open_ports": scan_res.get("open_ports", []),
            "services": services,
            "findings": findings,
            "local_bindings": local_bindings,
        }

    if targets:
        with ThreadPoolExecutor(max_workers=min(len(targets), max(1, args.max_workers))) as executor:
            future_map = {executor.submit(scan_one, t): t for t in targets}
            for fut in as_completed(future_map):
                t = future_map[fut]
                try:
                    results.append(fut.result())
                except Exception as e:
                    results.append(
                        {
                            "target": t,
                            "open_ports": [],
                            "services": [],
                            "findings": [],
                            "local_bindings": {},
                            "error": str(e),
                        }
                    )

        results.sort(key=lambda x: x.get("target", ""))

    print("\n" + "=" * 40)
    print(" SCAN REPORT ")
    print("=" * 40)

    severities = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0, "unknown": 0}
    for r in results:
        print(f"Target: {r['target']}")
        if r.get("error"):
            print(f"  Scan error: {r.get('error')}")
            continue
        if not r.get("open_ports"):
            print("  No open ports found.")
            continue
        print(f"  Open ports: {r['open_ports']}")
        if r.get("local_bindings"):
            for p, binds in r["local_bindings"].items():
                if binds:
                    addrs = ", ".join(sorted({b.get('local_address', '') for b in binds if b.get('local_address')}))
                    print(f"  Local bindings for {p}: {addrs}")
        if not r.get("findings"):
            print("  No OpenClaw services identified.")
            continue
        for f in r["findings"]:
            vlist = f.get("vulnerabilities", [])
            if not vlist:
                print(f"  Service: {f.get('target')} - No vulnerabilities found.")
                continue
            print(f"  Service: {f.get('target')}")
            for v in vlist:
                sev = (v.get("severity") or "Unknown").lower()
                sev_key = sev if sev in severities else "unknown"
                severities[sev_key] += 1
                print(f"    [{v.get('severity','Unknown')}] {v.get('type','')}")

    if local_audit_results:
        print(f"Local Audit Findings:")
        for f in local_audit_results["findings"]:
            print(f"    [{f.get('severity')}] {f.get('type')}: {f.get('details')}")

    json_path = out_dir / f"{report_base}.json"
    try:
        report_data = {
            "results": results
        }
        if local_audit_results:
            report_data["local_audit"] = local_audit_results
            
        json_path.write_text(json.dumps(report_data, indent=4, ensure_ascii=False), encoding="utf-8")
        print(f"\n[+] Detailed report saved to {json_path.as_posix()}")
    except Exception as e:
        print(f"[-] Failed to save report: {e}")

    if not args.no_html:
        html_path = out_dir / f"{report_base}.html"
        try:
            total_targets = len(results)
            total_services = sum(len(r.get("findings", [])) for r in results)
            total_open_ports = sum(len(r.get("open_ports", [])) for r in results)
            
            # Add audit findings to severities
            if local_audit_results:
                for f in local_audit_results["findings"]:
                    sev = (f.get("severity") or "Unknown").lower()
                    sev_key = sev if sev in severities else "unknown"
                    severities[sev_key] += 1
            
            def _is_private_or_local(host):
                h = (host or "").strip().lower()
                if h in ("127.0.0.1", "localhost", "::1"):
                    return True
                parts = h.split(".")
                if len(parts) == 4 and all(p.isdigit() for p in parts):
                    a, b, c, d = [int(x) for x in parts]
                    if a == 10:
                        return True
                    if a == 192 and b == 168:
                        return True
                    if a == 172 and 16 <= b <= 31:
                        return True
                    if a == 127:
                        return True
                return False

            def _default_lang():
                if results:
                    return "zh" if _is_private_or_local(results[0].get("target")) else "en"
                return "zh"

            def _health_level():
                if severities.get("critical", 0) > 0 or severities.get("high", 0) > 0:
                    return "red"
                if severities.get("medium", 0) > 0:
                    return "yellow"
                return "green"

            local_cli_version = None
            if local_audit_results and isinstance(local_audit_results, dict):
                raw = local_audit_results.get("raw") or {}
                if isinstance(raw, dict):
                    oc = raw.get("openclaw") or {}
                    if isinstance(oc, dict):
                        local_cli_version = oc.get("version") or None

            sev_kpis = [
                ("critical", severities.get("critical", 0)),
                ("high", severities.get("high", 0)),
                ("medium", severities.get("medium", 0)),
                ("low", severities.get("low", 0)),
                ("info", severities.get("info", 0)),
                ("unknown", severities.get("unknown", 0)),
            ]
            kpi_html = "".join([f"<div class='kpi'><div class='k' data-k='sev_{k}'></div><div class='v'>{v}</div></div>" for k, v in sev_kpis])

            recos = []
            def _add_reco(k, zh, en):
                recos.append({"k": k, "zh": zh, "en": en})
            red_types = []
            red_seen = set()
            def _is_red(sev):
                s = str(sev or "").strip().lower()
                return s in ("critical", "high")
            def _add_red_type(t):
                tt = str(t or "").strip()
                if not tt:
                    return
                if tt in red_seen:
                    return
                red_seen.add(tt)
                red_types.append(tt)
            for r in results:
                for f in r.get("findings", []) or []:
                    for v in f.get("vulnerabilities", []) or []:
                        if _is_red(v.get("severity")):
                            _add_red_type(v.get("type"))
            if local_audit_results:
                for f in local_audit_results.get("findings", []) or []:
                    if _is_red(f.get("severity")):
                        _add_red_type(f.get("type"))

            for t in red_types:
                if t == "weak_credentials":
                    _add_reco("weak_credentials", "立刻修改默认口令，禁用弱口令/默认账号，并开启 MFA（如支持）。", "Change default credentials immediately, disable default accounts, and enable MFA if available.")
                elif t in ("openclaw_outdated", "openclaw_version_mismatch"):
                    _add_reco("openclaw_outdated", "升级 OpenClaw 到最新稳定版本并谨慎验证：升级后部分或全部功能可能不可用，请结合自身情况判断。", "Upgrade OpenClaw to the latest stable release and validate carefully: after upgrading, some or all functions may be unavailable; assess carefully.")
                elif t == "windows_support_status":
                    _add_reco("windows_support_status", "Windows 已超出支持周期：建议优先评估升级到 Windows 11；若无法升级，请考虑注册 Windows 10 ESU 计划以持续获取安全更新至 2026-10。", "Windows is out of support: consider upgrading to Windows 11; if not eligible, enroll in Windows 10 ESU to continue receiving security updates until 2026-10.")
                elif t == "windows_cve_unpatched":
                    _add_reco("windows_cve_unpatched", "按报告列出的 KB 安装系统更新，并在安装后重新审计验证。", "Install the missing Windows updates (KBs) and rerun the audit to verify.")
                elif t == "windows_kb_map_missing":
                    _add_reco("windows_kb_map_missing", "先生成 CVE↔KB 映射文件（MSRC CVRF），再做补丁核验。", "Generate a CVE↔KB mapping from MSRC CVRF first, then validate patch status.")
                elif t == "unknown_version":
                    _add_reco("unknown_version", "让服务暴露版本信息（如 X-OpenClaw-Version 或 /api/status），便于自动化风控。", "Expose service version (e.g., X-OpenClaw-Version or /api/status) to enable automated risk checks.")
                else:
                    _add_reco(t, f"发现高风险项：{t}。请参考报告详情，尽快采取缓解/修复措施并复核。", f"High-risk finding detected: {t}. Refer to report details, remediate, and re-verify.")
            if not recos:
                _add_reco("ok", "当前未发现高风险项，建议保持系统与 OpenClaw 定期更新，并持续最小暴露面。", "No high-risk issues detected. Keep OS/OpenClaw updated and continue minimizing exposure.")

            cards = []

            if local_audit_results:
                items = []
                for f in local_audit_results["findings"]:
                    sev = f.get("severity", "Unknown")
                    sev_cls = str(sev).lower()
                    det = f.get("details", "")
                    items.append(
                        f"<li>"
                        f"<div class='row'>"
                        f"<span class='sev sev-{_h(sev_cls)}' data-sev='{_h(sev_cls)}'>{_h(sev)}</span>"
                        f"<span class='type'>{_h(f.get('type',''))}</span>"
                        f"</div>"
                        f"<div class='details'>{_h(det)}</div>"
                        f"</li>"
                    )
                meta_parts = [f"<span data-k='local_host'></span>: {_h(audit.get_os_info().get('system'))}"]
                if local_cli_version:
                    meta_parts.append(f"<span data-k='local_openclaw_cli'></span>: {_h(local_cli_version)}")
                cards.append(
                    f"<div class='card'>"
                    f"<div class='card-head'>"
                    f"<div class='card-title' data-k='local_audit_title'></div>"
                    f"<div class='card-meta'>{' · '.join(meta_parts)}</div>"
                    f"</div>"
                    f"<div class='section'>"
                    f"<div class='label' data-k='audit_findings'></div>"
                    f"<ul class='vuln'>{''.join(items)}</ul>"
                    f"</div>"
                    f"</div>"
                )

            for r in results:
                binds_html = ""
                if r.get("local_bindings"):
                    parts = []
                    for p, binds in r["local_bindings"].items():
                        if not binds:
                            continue
                        addrs = ", ".join(sorted({b.get("local_address", "") for b in binds if b.get("local_address")}))
                        parts.append(f"<div class='sub'><span data-k='port'></span> {_h(p)}: {_h(addrs)}</div>")
                    if parts:
                        binds_html = "<div class='section'><div class='label' data-k='local_bindings'></div>" + "".join(parts) + "</div>"

                open_ports_html = ", ".join(str(p) for p in r.get("open_ports", [])) or "-"
                err = r.get("error")
                err_html = f"<div class='err'>{_h(err)}</div>" if err else ""
                findings = r.get("findings", [])
                if err:
                    vuln_html = "<div class='ok' data-k='no_results'></div>"
                elif not findings:
                    vuln_html = "<div class='ok' data-k='no_openclaw'></div>"
                else:
                    items = []
                    for f in findings:
                        vlist = f.get("vulnerabilities", [])
                        svc = f.get("service", "") or ""
                        svc_target = f.get("target", "") or ""
                        svc_version = f.get("version", "") or ""
                        svc_version_norm = str(svc_version).strip()
                        if svc_version_norm.lower() in ("unknown", "none", ""):
                            svc_version_html = f"<span class='muted' data-k='version_not_exposed'></span>"
                        else:
                            svc_version_html = _h(svc_version_norm)

                        extra_meta = ""
                        if _is_private_or_local(r.get("target")) and local_cli_version:
                            if svc_version_norm.lower() in ("unknown", "none", ""):
                                extra_meta = f"<div class='svc-sub'><span data-k='local_openclaw_cli'></span>: {_h(local_cli_version)}</div>"

                        header = (
                            f"<div class='svc'>"
                            f"<div class='svc-left'>"
                            f"<div class='svc-title'>{_h(svc)}</div>"
                            f"<div class='svc-meta'>{_h(svc_target)}</div>"
                            f"{extra_meta}"
                            f"</div>"
                            f"<div class='svc-right'>"
                            f"<div class='svc-k' data-k='service_version'></div>"
                            f"<div class='svc-v'>{svc_version_html}</div>"
                            f"</div>"
                            f"</div>"
                        )
                        if not vlist:
                            items.append(header + "<div class='ok' data-k='no_vulns'></div>")
                            continue
                        li = []
                        for v in vlist:
                            sev = v.get("severity", "Unknown")
                            sev_cls = str(sev).lower()
                            det = v.get("details", "")
                            cves = ", ".join(v.get("cves", [])) if v.get("cves") else ""
                            hits = ""
                            if v.get("hits"):
                                hit_lines = []
                                for h in v["hits"]:
                                    kw_list = h.get("keywords", [])
                                    kw_list = kw_list if isinstance(kw_list, list) else [str(kw_list)]
                                    hit_lines.append(f"<div class='hit'><span class='path'>{_h(h.get('path',''))}</span><span class='kw'>{_h(', '.join([str(x) for x in kw_list]))}</span></div>")
                                hits = "<div class='hits'>" + "".join(hit_lines) + "</div>"
                            cve_html = f"<div class='cves'>{_h(cves)}</div>" if cves else ""
                            det_html = f"<div class='details'>{_h(det)}</div>" if det else ""
                            li.append(
                                f"<li>"
                                f"<div class='row'>"
                                f"<span class='sev sev-{_h(sev_cls)}' data-sev='{_h(sev_cls)}'>{_h(sev)}</span>"
                                f"<span class='type'>{_h(v.get('type',''))}</span>"
                                f"</div>"
                                f"{det_html}{cve_html}{hits}"
                                f"</li>"
                            )
                        items.append(header + "<ul class='vuln'>" + "".join(li) + "</ul>")
                    vuln_html = "".join(items)

                cards.append(
                    f"<div class='card'>"
                    f"<div class='card-head'>"
                    f"<div class='card-title'>{_h(r.get('target',''))}</div>"
                    f"<div class='card-meta'><span data-k='open_ports'></span>: {_h(open_ports_html)}</div>"
                    f"</div>"
                    f"{err_html}"
                    f"{binds_html}"
                    f"<div class='section'><div class='label' data-k='findings'></div>{vuln_html}</div>"
                    f"</div>"
                )

            lang = _default_lang()
            health = _health_level()
            reco_json = json.dumps(recos, ensure_ascii=False)

            html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OpenClaw Scan Report</title>
  <style>
    :root {{
      --bg1:#f5f7ff;
      --bg2:#f7f8fa;
      --card:#ffffffcc;
      --border:#e7e9ee;
      --text:#0b0f19;
      --muted:#6b7280;
      --shadow:0 10px 30px rgba(12, 20, 40, .08);
      --shadow2:0 1px 2px rgba(12, 20, 40, .06);
      --r:18px;
      --red:#ff3b30;
      --yellow:#ffcc00;
      --green:#34c759;
      --blue:#0a84ff;
    }}
    html,body{{height:100%}}
    body{{
      margin:0;
      padding:28px;
      color:var(--text);
      background:radial-gradient(1200px 600px at 20% 0%, var(--bg1), transparent),
                 radial-gradient(1200px 600px at 90% 10%, #fdf2ff, transparent),
                 linear-gradient(180deg, var(--bg2), #ffffff);
      font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Segoe UI",Roboto,Helvetica,Arial,"Apple Color Emoji","Segoe UI Emoji";
    }}
    .wrap{{max-width:1100px;margin:0 auto}}
    .topbar{{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-bottom:18px}}
    .title h1{{margin:0;font-size:22px;letter-spacing:-.02em}}
    .sub{{color:var(--muted);font-size:12px}}
    .actions{{display:flex;gap:10px;align-items:center}}
    .btn{{
      border:1px solid var(--border);
      background:rgba(255,255,255,.9);
      border-radius:999px;
      padding:8px 12px;
      font-size:12px;
      cursor:pointer;
      box-shadow:var(--shadow2);
    }}
    .summary{{display:grid;grid-template-columns:1.3fr 1fr;gap:14px;align-items:stretch;margin-bottom:18px}}
    @media (max-width:900px){{.summary{{grid-template-columns:1fr}}}}
    .panel{{
      background:var(--card);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border:1px solid var(--border);
      border-radius:var(--r);
      box-shadow:var(--shadow);
      padding:16px;
    }}
    .health{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
    .dot{{width:12px;height:12px;border-radius:50%}}
    .dot.red{{background:var(--red);box-shadow:0 0 0 6px rgba(255,59,48,.14)}}
    .dot.yellow{{background:var(--yellow);box-shadow:0 0 0 6px rgba(255,204,0,.14)}}
    .dot.green{{background:var(--green);box-shadow:0 0 0 6px rgba(52,199,89,.14)}}
    .health-title{{font-weight:700}}
    .health-text{{color:var(--muted);font-size:12px}}
    .kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
    @media (max-width:520px){{.kpis{{grid-template-columns:repeat(2,1fr)}}}}
    .kpi{{background:rgba(255,255,255,.7);border:1px solid var(--border);border-radius:14px;padding:10px 12px}}
    .kpi .k{{color:var(--muted);font-size:12px}}
    .kpi .v{{font-size:20px;font-weight:800;letter-spacing:-.02em}}
    .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:14px}}
    .card{{
      background:var(--card);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border:1px solid var(--border);
      border-radius:var(--r);
      padding:16px;
      box-shadow:var(--shadow);
    }}
    .card-head{{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:10px}}
    .card-title{{font-weight:800;color:#0b2540;word-break:break-all}}
    .card-meta{{color:var(--muted);font-size:12px;word-break:break-all}}
    .label{{font-weight:800;margin:14px 0 8px 0}}
    .section{{margin-top:8px}}
    .err{{color:#b42318;background:rgba(255,59,48,.08);border:1px solid rgba(255,59,48,.18);padding:10px 12px;border-radius:14px;font-size:12px;font-weight:700;word-break:break-all}}
    .ok{{color:#1f7a3d;font-weight:800}}
    .muted{{color:var(--muted)}}
    ul.vuln{{margin:0;padding-left:18px}}
    ul.vuln li{{margin:10px 0}}
    .row{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
    .sev{{display:inline-flex;align-items:center;justify-content:center;min-width:64px;padding:2px 10px;border-radius:999px;font-size:12px;color:#fff;font-weight:800}}
    .sev-critical{{background:var(--red)}}
    .sev-high{{background:#ff9500}}
    .sev-medium{{background:var(--blue)}}
    .sev-low{{background:var(--green)}}
    .sev-info{{background:#64748b}}
    .sev-unknown{{background:#8e8e93}}
    .type{{font-weight:800}}
    .details{{font-size:12px;color:var(--muted);margin-top:4px;word-break:break-word}}
    .cves{{font-size:12px;color:#111827;margin-top:4px;word-break:break-word}}
    .svc{{display:flex;gap:12px;justify-content:space-between;align-items:flex-start;padding:12px 12px;border:1px solid var(--border);border-radius:16px;background:rgba(255,255,255,.65);margin:12px 0 10px 0}}
    .svc-title{{font-weight:900}}
    .svc-meta{{font-size:12px;color:var(--muted);word-break:break-all}}
    .svc-sub{{font-size:12px;color:var(--muted);margin-top:2px}}
    .svc-right{{text-align:right;min-width:160px}}
    .svc-k{{font-size:12px;color:var(--muted)}}
    .svc-v{{font-size:14px;font-weight:900}}
    .hits{{margin-top:8px;border-left:3px solid rgba(107,114,128,.25);padding-left:10px}}
    .hit{{font-size:12px;color:#111827;margin:3px 0}}
    .hit .path{{display:inline-block;min-width:110px;color:#0a66c2}}
    .hit .kw{{color:var(--muted)}}
    .reco li{{margin:8px 0}}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div class="title">
        <h1 data-k="title"></h1>
        <div class="sub" data-k="subtitle"></div>
      </div>
      <div class="actions">
        <button class="btn" id="langBtn"></button>
      </div>
    </div>

    <div class="summary">
      <div class="panel">
        <div class="health">
          <div class="dot {health}"></div>
          <div>
            <div class="health-title" id="healthTitle"></div>
            <div class="health-text" id="healthText"></div>
          </div>
        </div>
        <div class="sub">
          <span data-k="run"></span>: {_h(run_id)} · <span data-k="targets"></span>: {total_targets} · <span data-k="services"></span>: {total_services} · <span data-k="open_ports"></span>: {total_open_ports}
        </div>
      </div>
      <div class="panel">
        <div class="label" data-k="overall_counts"></div>
        <div class="kpis">{kpi_html}</div>
      </div>
    </div>

    <div class="panel" style="margin-bottom:14px">
      <div class="label" data-k="next_steps"></div>
      <ul class="reco" id="recoList"></ul>
    </div>

    <div class="cards">{''.join(cards)}</div>
  </div>

  <script>
    const DEFAULT_LANG = "{lang}";
    const HEALTH = "{health}";
    const RECO = {reco_json};
    const I18N = {{
      zh: {{
        title: "OpenClaw 扫描报告",
        subtitle: "健康概览 · 详细结果 · 下一步建议",
        run: "运行",
        targets: "目标",
        services: "服务",
        open_ports: "开放端口",
        overall_counts: "总体统计",
        next_steps: "下一步建议",
        findings: "详细内容",
        local_audit_title: "本机审计",
        audit_findings: "审计发现",
        local_host: "主机",
        local_openclaw_cli: "本机 OpenClaw CLI",
        local_bindings: "本地监听",
        port: "端口",
        no_results: "无结果（扫描异常）",
        no_openclaw: "未识别到 OpenClaw 服务",
        no_vulns: "未发现漏洞",
        service_version: "服务版本",
        version_not_exposed: "未暴露",
        sev_critical: "严重",
        sev_high: "高",
        sev_medium: "中",
        sev_low: "低",
        sev_info: "信息",
        sev_unknown: "未知",
        lang_btn: "English",
        health_red_title: "需要立即处理",
        health_red_text: "存在高危/严重风险项，建议优先修复。",
        health_yellow_title: "需要关注",
        health_yellow_text: "存在中等风险项，建议安排修复与复核。",
        health_green_title: "总体健康",
        health_green_text: "未发现高风险项，保持更新与最小暴露面。",
      }},
      en: {{
        title: "OpenClaw Scan Report",
        subtitle: "Health overview · Details · Next steps",
        run: "Run",
        targets: "Targets",
        services: "Services",
        open_ports: "Open ports",
        overall_counts: "Overall counts",
        next_steps: "Next steps",
        findings: "Details",
        local_audit_title: "Local Audit",
        audit_findings: "Audit findings",
        local_host: "Host",
        local_openclaw_cli: "Local OpenClaw CLI",
        local_bindings: "Local bindings",
        port: "Port",
        no_results: "No results (scan error)",
        no_openclaw: "No OpenClaw service identified",
        no_vulns: "No vulnerabilities found",
        service_version: "Service version",
        version_not_exposed: "Not exposed",
        sev_critical: "Critical",
        sev_high: "High",
        sev_medium: "Medium",
        sev_low: "Low",
        sev_info: "Info",
        sev_unknown: "Unknown",
        lang_btn: "中文",
        health_red_title: "Immediate action needed",
        health_red_text: "High/Critical items detected. Fix these first.",
        health_yellow_title: "Attention required",
        health_yellow_text: "Medium-risk items detected. Schedule remediation and verify.",
        health_green_title: "Overall healthy",
        health_green_text: "No high-risk items detected. Keep things updated and minimize exposure.",
      }}
    }};

    let lang = DEFAULT_LANG;

    function applyLang() {{
      document.querySelectorAll("[data-k]").forEach(el => {{
        const k = el.getAttribute("data-k");
        const v = (I18N[lang] || {{}})[k];
        if (typeof v === "string") el.textContent = v;
      }});
      document.querySelectorAll("[data-sev]").forEach(el => {{
        const s = (el.getAttribute("data-sev") || "unknown").toLowerCase();
        const mapKey = "sev_" + (["critical","high","medium","low","info","unknown"].includes(s) ? s : "unknown");
        const v = (I18N[lang] || {{}})[mapKey];
        if (typeof v === "string") el.textContent = v;
      }});

      const btn = document.getElementById("langBtn");
      btn.textContent = (I18N[lang] || {{}}).lang_btn || "EN";

      const ht = document.getElementById("healthTitle");
      const hx = document.getElementById("healthText");
      const key = HEALTH === "red" ? "red" : (HEALTH === "yellow" ? "yellow" : "green");
      ht.textContent = (I18N[lang] || {{}})[`health_${{key}}_title`] || "";
      hx.textContent = (I18N[lang] || {{}})[`health_${{key}}_text`] || "";

      const recoList = document.getElementById("recoList");
      recoList.innerHTML = "";
      for (const r of (RECO || [])) {{
        const li = document.createElement("li");
        li.textContent = (lang === "zh" ? r.zh : r.en) || "";
        recoList.appendChild(li);
      }}
    }}

    document.getElementById("langBtn").addEventListener("click", () => {{
      lang = (lang === "zh" ? "en" : "zh");
      applyLang();
    }});

    applyLang();
  </script>
</body>
</html>"""
            html_path.write_text(html, encoding="utf-8")
            print(f"[+] HTML report saved to {html_path.as_posix()}")
        except Exception as e:
            print(f"[-] Failed to save HTML report: {e}")

    exit_code = 0
    if severities["critical"] > 0 or severities["high"] > 0:
        exit_code = 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
