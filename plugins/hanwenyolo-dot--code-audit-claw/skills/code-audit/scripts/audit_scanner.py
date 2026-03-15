#!/usr/bin/env python3
"""
code-audit scanner — OpenClaw Skill
扫描代码文件或灵魂文件，输出分级审计报告

支持参数：
  --mode   security | quality | soul | all | system
  --html   生成 HTML 报告到桌面（~/Desktop）
  --ai     在末尾打印 AI Analysis Prompt 区块供 Claude 分析
"""

import re
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
import html as html_mod

# ── 规则定义 ──────────────────────────────────────────────────────────────────

SECURITY_RULES = [
    # (name, pattern, severity, message)
    ("hardcoded_secret",    r'(?i)(api_key|secret|password|token)\s*=\s*["\'][^"\']{8,}',
     "🔴 CRITICAL", "疑似硬编码密钥/密码"),
    ("openai_key",          r'sk-[a-zA-Z0-9]{20,}',
     "🔴 CRITICAL", "疑似 OpenAI API Key 泄露"),
    ("bearer_token",        r'Bearer\s+[a-zA-Z0-9\-_\.]{20,}',
     "🔴 CRITICAL", "疑似 Bearer Token 泄露"),
    ("rm_rf",               r'rm\s+-[rf]+\s+/',
     "🔴 CRITICAL", "危险的 rm -rf 命令"),
    ("eval_exec",           r'\b(eval|exec)\s*\(',
     "🔴 CRITICAL", "使用了 eval/exec，存在代码注入风险"),
    ("sql_concat",          r'["\']SELECT.+["\'\+]\s*\w+',
     "🔴 CRITICAL", "SQL 字符串拼接，存在注入风险"),
    ("pickle_loads",        r'pickle\.loads\(',
     "🟡 WARNING",  "pickle.loads 反序列化不安全数据有风险"),
    ("yaml_unsafe",         r'yaml\.load\(',
     "🟡 WARNING",  "yaml.load 应使用 Loader=yaml.SafeLoader"),
    ("bare_except",         r'except\s*:',
     "🟢 INFO",     "裸 except 会吞掉所有异常，建议指定异常类型"),
    # 新规则：环境变量 fallback 硬编码
    ("env_fallback_hardcoded",
     r'os\.environ\.get\(\s*["\'][^"\']+["\']\s*,\s*["\'][^"\']{4,}["\']\s*\)',
     "🟡 WARNING",
     "os.environ.get() 使用了硬编码 fallback 值，密钥/密码可能以默认值暴露；建议改用 os.environ['KEY'] 强制显式配置"),
]

QUALITY_RULES = [
    ("long_line",           r'.{150,}',
     "🟢 INFO",     "行超过 150 字符，建议拆分"),
    ("magic_number",        r'\b(?<!\.)(?!0|1|2|100)\d{2,}\b',
     "🟢 INFO",     "魔法数字，建议定义为常量"),
    ("todo_fixme",          r'(?i)(TODO|FIXME|HACK|XXX)',
     "🟢 INFO",     "存在 TODO/FIXME 注释，需跟踪处理"),
    ("dead_return",         r'return\s+\w+\n\s+\w',
     "🟡 WARNING",  "return 后仍有代码（不可达代码）"),
]

SOUL_RULES = [
    ("missing_no_restart",  r'gateway restart',
     "🔴 CRITICAL", "未找到「网关重启铁律」关键词 — 铁律可能缺失"),
    ("missing_communicate", r'先沟通|communicate.first|沟通铁律',
     "🔴 CRITICAL", "未找到「先沟通铁律」关键词 — 铁律可能缺失"),
    ("missing_handchop",    r'剁手|hand.chop|PAUSE_FOR_CONFIRMATION',
     "🔴 CRITICAL", "未找到「剁手规则」关键词 — 铁律可能缺失"),
    ("plaintext_key",       r'(?i)(api_key|token|secret|password)\s*[:=]\s*[a-zA-Z0-9\-_]{20,}',
     "🔴 CRITICAL", "疑似明文 API Key/Token 存储在配置文件中"),
    ("memory_oversize",     None,
     "🟡 WARNING",  "MEMORY.md 超过 15K 字符，建议触发 memory-maintenance 压缩"),
    ("no_last_updated",     r'Last Updated|最后更新',
     "🟢 INFO",     "未找到版本/更新日期记录"),
    # AGENTS.md 完整性检查
    ("missing_subagent_rule",  r'sub.?agent|分身|派发',
     "🟡 WARNING", "AGENTS.md 未找到 Sub-agent 调度规则 — 建议补充"),
    ("missing_workflow_rule",  r'Research.*Plan.*Confirm|五步工作流|vibe.?coding',
     "🟡 WARNING", "AGENTS.md 未找到五步工作流规则 — 建议补充"),
]

# ── 扫描逻辑 ──────────────────────────────────────────────────────────────────

def scan_code_file(filepath, mode="security"):
    issues = []
    rules = SECURITY_RULES if mode == "security" else QUALITY_RULES
    if mode == "all":
        rules = SECURITY_RULES + QUALITY_RULES

    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
    except Exception as e:
        return [{"file": str(filepath), "line": 0, "severity": "🟡 WARNING",
                 "rule": "read_error", "message": f"无法读取文件: {e}", "snippet": ""}]

    for lineno, line in enumerate(lines, 1):
        for rule_name, pattern, severity, message in rules:
            if pattern and re.search(pattern, line):
                issues.append({
                    "file": str(filepath),
                    "line": lineno,
                    "severity": severity,
                    "rule": rule_name,
                    "message": message,
                    "snippet": line.strip()[:100],
                })
    return issues


def scan_soul_file(filepath):
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return [{"file": str(filepath), "line": 0, "severity": "🟡 WARNING",
                 "rule": "read_error", "message": f"无法读取文件: {e}", "snippet": ""}]

    fname = filepath.name.upper()

    for rule_name, pattern, severity, message in SOUL_RULES:
        if rule_name == "memory_oversize":
            if "MEMORY" in fname and len(content) > 15000:
                issues.append({
                    "file": str(filepath), "line": 0,
                    "severity": severity, "rule": rule_name,
                    "message": f"{message} (当前 {len(content)} 字符)",
                    "snippet": ""
                })
            continue

        if rule_name in ("missing_no_restart", "missing_communicate", "missing_handchop"):
            if "SOUL" in fname and not re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    "file": str(filepath), "line": 0,
                    "severity": severity, "rule": rule_name,
                    "message": message, "snippet": ""
                })
            continue

        if rule_name in ("missing_subagent_rule", "missing_workflow_rule"):
            if "AGENTS" in fname and not re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    "file": str(filepath), "line": 0,
                    "severity": severity, "rule": rule_name,
                    "message": message, "snippet": ""
                })
            continue

        if rule_name == "no_last_updated":
            if not re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    "file": str(filepath), "line": 0,
                    "severity": severity, "rule": rule_name,
                    "message": message, "snippet": ""
                })
            continue

        if pattern:
            for lineno, line in enumerate(content.splitlines(), 1):
                if re.search(pattern, line):
                    issues.append({
                        "file": str(filepath), "line": lineno,
                        "severity": severity, "rule": rule_name,
                        "message": message,
                        "snippet": line.strip()[:80]
                    })

    return issues


# ── System 安全检查 ───────────────────────────────────────────────────────────

# 系统命令白名单（及其验签期望）
SYSTEM_CMDS_TO_CHECK = [
    "/bin/ls", "/bin/ps", "/bin/cat", "/bin/chmod",
    "/usr/bin/top", "/usr/bin/find", "/usr/bin/curl",
]

# 已知 SUID/SGID 白名单（macOS 正常系统文件）
SUID_WHITELIST = {
    "/usr/bin/su",
    "/usr/bin/sudo",
    "/usr/bin/login",
    "/usr/bin/newgrp",
    "/usr/bin/at",
    "/usr/bin/atq",
    "/usr/bin/atrm",
    "/usr/bin/batch",
    "/usr/bin/top",
    "/usr/bin/write",
    "/usr/bin/crontab",
    "/usr/bin/quota",
    "/usr/bin/passwd",
    "/usr/bin/rsh",
    "/usr/bin/rcp",
    "/usr/bin/rlogin",
    "/usr/sbin/traceroute",
    "/usr/sbin/traceroute6",
    "/usr/sbin/postqueue",
    "/usr/sbin/postdrop",
    "/usr/lib/sa/sadc",
    "/usr/libexec/security_authtrampoline",
    "/usr/libexec/authopen",
    "/sbin/mount_nfs",
    "/sbin/umount",
    "/bin/ps",
    "/usr/lib/dma/dma-mbox-create",
}

# 网络监听端口白名单
LISTEN_PORT_WHITELIST = {
    "22", "80", "443", "3000", "3001", "8080", "8443",
    "8888", "9000", "18789", "5000", "4000", "1080",
    "49152", "49153",  # macOS 动态端口
}

# 敏感启动项可疑内容正则
SUSPICIOUS_PATTERNS = [
    (r'curl\s+.*\|\s*(bash|sh|zsh|python)', "🔴 CRITICAL",
     "疑似远程下载执行（curl | bash 模式）"),
    (r'wget\s+.*\|\s*(bash|sh|zsh|python)', "🔴 CRITICAL",
     "疑似远程下载执行（wget | bash 模式）"),
    (r'base64\s+(-d|--decode)\s*\|?\s*(bash|sh|python|eval)', "🔴 CRITICAL",
     "疑似 base64 解码执行（反序列化木马特征）"),
    (r'eval\s*\(\s*(base64|curl|wget)', "🔴 CRITICAL",
     "疑似动态 eval 执行外部内容"),
    (r'/dev/tcp/\d+\.\d+\.\d+\.\d+/\d+', "🔴 CRITICAL",
     "疑似反弹 Shell（/dev/tcp 特征）"),
    (r'bash\s+-i\s+>&\s*/dev/tcp', "🔴 CRITICAL",
     "疑似反弹 Shell（bash -i >& /dev/tcp 特征）"),
    (r'nc\s+(-e|--exec|-c)\s+/bin/(bash|sh)', "🔴 CRITICAL",
     "疑似 netcat 反弹 Shell"),
    (r'chmod\s+\+x\s+/tmp/', "🟡 WARNING",
     "在 /tmp 目录设置可执行权限，存在潜在风险"),
    (r'export\s+PATH=.*:/tmp', "🟡 WARNING",
     "PATH 包含 /tmp 目录，可能被恶意程序劫持"),
    (r'(rm\s+-rf\s+~|rm\s+-rf\s+/)', "🔴 CRITICAL",
     "危险的 rm -rf 命令（删除家目录或根目录）"),
]


def scan_system_command_integrity():
    """1. 系统命令完整性检查（codesign 验签）"""
    issues = []
    for cmd in SYSTEM_CMDS_TO_CHECK:
        if not os.path.exists(cmd):
            continue
        try:
            result = subprocess.run(
                ["codesign", "-v", cmd],
                capture_output=True, text=True, timeout=10
            )
            # codesign -v 验签成功时 returncode=0，失败时非0
            if result.returncode != 0:
                issues.append({
                    "file": cmd,
                    "line": 0,
                    "severity": "🔴 CRITICAL",
                    "rule": "system_cmd_codesign_fail",
                    "message": f"系统命令代码签名验证失败: {result.stderr.strip()[:100]}",
                    "snippet": f"codesign -v {cmd} → returncode={result.returncode}",
                })
        except subprocess.TimeoutExpired:
            issues.append({
                "file": cmd, "line": 0, "severity": "🟡 WARNING",
                "rule": "system_cmd_codesign_timeout",
                "message": "codesign 验签超时，跳过此命令",
                "snippet": cmd,
            })
        except Exception as e:
            issues.append({
                "file": cmd, "line": 0, "severity": "🟢 INFO",
                "rule": "system_cmd_codesign_skip",
                "message": f"codesign 检查跳过: {e}",
                "snippet": cmd,
            })
    return issues


def scan_startup_items():
    """2. 敏感启动项检查（shell rc 文件 + LaunchAgents plist）"""
    issues = []
    home = Path.home()

    # 检查 shell 配置文件
    shell_files = [
        home / ".zshrc",
        home / ".bashrc",
        home / ".bash_profile",
        home / ".zprofile",
        home / ".profile",
    ]

    for fpath in shell_files:
        if not fpath.exists():
            continue
        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern, severity, message in SUSPICIOUS_PATTERNS:
            for lineno, line in enumerate(content.splitlines(), 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "file": str(fpath),
                        "line": lineno,
                        "severity": severity,
                        "rule": "suspicious_startup_item",
                        "message": message,
                        "snippet": line.strip()[:100],
                    })

    # 检查 LaunchAgents plist 文件
    launch_agents_dir = home / "Library" / "LaunchAgents"
    if launch_agents_dir.exists():
        for plist_file in launch_agents_dir.glob("*.plist"):
            try:
                content = plist_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for pattern, severity, message in SUSPICIOUS_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append({
                        "file": str(plist_file),
                        "line": 0,
                        "severity": severity,
                        "rule": "suspicious_launch_agent",
                        "message": f"LaunchAgent plist 含可疑内容: {message}",
                        "snippet": plist_file.name,
                    })

    return issues


def scan_network_listeners():
    """3. 异常网络监听检查"""
    issues = []
    try:
        # 尝试多个可能的 lsof 路径（macOS 下常在 /usr/sbin/lsof）
        lsof_path = "lsof"
        for candidate in ["/usr/sbin/lsof", "/usr/bin/lsof", "lsof"]:
            if os.path.exists(candidate):
                lsof_path = candidate
                break
        result = subprocess.run(
            [lsof_path, "-iTCP", "-sTCP:LISTEN", "-P", "-n"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0 and not result.stdout.strip():
            return issues

        lines = result.stdout.splitlines()
        seen_ports = set()
        for line in lines[1:]:  # 跳过标题行
            parts = line.split()
            if len(parts) < 9:
                continue
            # 提取端口（格式：*:PORT 或 127.0.0.1:PORT）
            addr_field = parts[8]  # NAME 字段
            port_match = re.search(r':(\d+)\s*\(LISTEN\)', line)
            if not port_match:
                # 尝试另一种格式
                port_match = re.search(r':(\d+)$', addr_field)
            if not port_match:
                continue
            port = port_match.group(1)
            if port in seen_ports:
                continue
            seen_ports.add(port)

            if port not in LISTEN_PORT_WHITELIST:
                cmd_name = parts[0]
                pid = parts[1]
                issues.append({
                    "file": "network/listeners",
                    "line": 0,
                    "severity": "🟡 WARNING",
                    "rule": "unknown_listen_port",
                    "message": f"非白名单端口正在监听: :{port} (进程: {cmd_name} PID={pid})",
                    "snippet": line.strip()[:120],
                })
    except subprocess.TimeoutExpired:
        issues.append({
            "file": "network/listeners", "line": 0,
            "severity": "🟡 WARNING",
            "rule": "network_scan_timeout",
            "message": "lsof 网络监听扫描超时",
            "snippet": "",
        })
    except Exception as e:
        issues.append({
            "file": "network/listeners", "line": 0,
            "severity": "🟢 INFO",
            "rule": "network_scan_error",
            "message": f"网络监听检查跳过: {e}",
            "snippet": "",
        })
    return issues


def scan_suid_sgid():
    """4. SUID/SGID 可疑文件检查"""
    issues = []
    try:
        result = subprocess.run(
            ["find", "/usr", "/bin", "/sbin",
             "(", "-perm", "-4000", "-o", "-perm", "-2000", ")",
             "-type", "f"],
            capture_output=True, text=True, timeout=30
        )
        found_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        for fpath in found_files:
            if fpath not in SUID_WHITELIST:
                issues.append({
                    "file": fpath,
                    "line": 0,
                    "severity": "🟡 WARNING",
                    "rule": "suspicious_suid_sgid",
                    "message": f"发现非白名单 SUID/SGID 文件: {fpath}",
                    "snippet": fpath,
                })
    except subprocess.TimeoutExpired:
        issues.append({
            "file": "/usr /bin /sbin", "line": 0,
            "severity": "🟡 WARNING",
            "rule": "suid_scan_timeout",
            "message": "SUID/SGID 扫描超时（目录太大或权限限制）",
            "snippet": "",
        })
    except Exception as e:
        issues.append({
            "file": "/usr /bin /sbin", "line": 0,
            "severity": "🟢 INFO",
            "rule": "suid_scan_error",
            "message": f"SUID/SGID 检查跳过: {e}",
            "snippet": "",
        })
    return issues


def scan_recent_system_changes():
    """5. 系统关键目录近期修改检查（7 天内）"""
    issues = []
    system_dirs = ["/bin", "/usr/bin", "/sbin"]
    for sdir in system_dirs:
        if not os.path.exists(sdir):
            continue
        try:
            result = subprocess.run(
                ["find", sdir, "-maxdepth", "1", "-type", "f", "-mtime", "-7"],
                capture_output=True, text=True, timeout=15
            )
            changed_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
            if changed_files:
                file_list = ", ".join(changed_files[:5])
                suffix = f"（等共 {len(changed_files)} 个）" if len(changed_files) > 5 else ""
                issues.append({
                    "file": sdir,
                    "line": 0,
                    "severity": "🟡 WARNING",
                    "rule": "system_dir_recently_modified",
                    "message": f"{sdir} 下发现 {len(changed_files)} 个文件在 7 天内被修改（macOS 系统更新可能导致）",
                    "snippet": file_list + suffix,
                })
        except subprocess.TimeoutExpired:
            issues.append({
                "file": sdir, "line": 0,
                "severity": "🟢 INFO",
                "rule": "recent_change_scan_timeout",
                "message": f"{sdir} 近期修改扫描超时",
                "snippet": "",
            })
        except Exception as e:
            issues.append({
                "file": sdir, "line": 0,
                "severity": "🟢 INFO",
                "rule": "recent_change_scan_error",
                "message": f"近期修改检查跳过: {e}",
                "snippet": "",
            })
    return issues


def run_system_audit():
    """整合运行所有 system 模式检查"""
    all_issues = []
    print("🔍 [1/5] 系统命令完整性检查（codesign）...")
    all_issues.extend(scan_system_command_integrity())
    print("🔍 [2/5] 敏感启动项检查（shell rc + LaunchAgents）...")
    all_issues.extend(scan_startup_items())
    print("🔍 [3/5] 异常网络监听检查...")
    all_issues.extend(scan_network_listeners())
    print("🔍 [4/5] SUID/SGID 可疑文件检查...")
    all_issues.extend(scan_suid_sgid())
    print("🔍 [5/5] 系统关键目录近期修改检查...")
    all_issues.extend(scan_recent_system_changes())
    return all_issues


def scan_cron_jobs(target_dir):
    """扫描系统 crontab，检测无描述的 Cron Job"""
    issues = []
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            return issues
        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            # 检查是否是 cron 表达式行（包含 5 字段时间 + 命令）
            if re.match(r'^[\d\*/,\-]+\s+[\d\*/,\-]+\s+[\d\*/,\-]+\s+[\d\*/,\-]+\s+[\d\*/,\-]+\s+', stripped):
                # 检查上一行是否为注释
                prev_line = lines[i - 1].strip() if i > 0 else ""
                if not prev_line.startswith("#"):
                    issues.append({
                        "file": "crontab",
                        "line": i + 1,
                        "severity": "🟡 WARNING",
                        "rule": "cron_no_description",
                        "message": "无注释描述的 Cron Job — 建议在该行上方添加 # 注释说明用途",
                        "snippet": stripped[:100]
                    })
    except Exception as e:
        issues.append({
            "file": "crontab", "line": 0, "severity": "🟢 INFO",
            "rule": "cron_scan_error", "message": f"crontab 扫描跳过: {e}", "snippet": ""
        })
    return issues


def scan_skill_trigger_conflicts(target_dir):
    """扫描所有 SKILL.md，检测触发词冲突"""
    issues = []
    trigger_map = {}  # trigger_word -> [skill_paths]

    skill_files = list(Path(target_dir).rglob("SKILL.md"))
    if len(skill_files) < 2:
        return issues

    for skill_file in skill_files:
        try:
            content = skill_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 只从触发词标记行提取（避免从全文引号内容误报普通词）
        trigger_lines = re.findall(r'(?:触发词|Trigger(?:s)?\s*(?:on)?|Use when)[：:]\s*(.+)', content)
        words = set()
        for line in trigger_lines:
            parts = re.split(r'[,，、/|]', line)
            for p in parts:
                p = p.strip().strip('"\'「」""')
                if len(p) >= 2:
                    words.add(p.lower())

        for word in words:
            if word not in trigger_map:
                trigger_map[word] = []
            trigger_map[word].append(str(skill_file))

    for word, paths in trigger_map.items():
        if len(paths) >= 2:
            skills_list = ", ".join([Path(p).parent.name for p in paths])
            issues.append({
                "file": "skills/",
                "line": 0,
                "severity": "🟡 WARNING",
                "rule": "skill_trigger_conflict",
                "message": f"触发词「{word}」在多个 Skill 中重复出现: {skills_list}",
                "snippet": ""
            })

    return issues


def is_soul_file(filepath):
    soul_names = {"SOUL.MD", "MEMORY.MD", "AGENTS.MD", "HEARTBEAT.MD",
                  "USER.MD", "TOOLS.MD", "IDENTITY.MD", "SKILL.MD"}
    return filepath.name.upper() in soul_names


def collect_files(target):
    p = Path(target).expanduser()
    if p.is_file():
        return [p]
    exts = {".py", ".js", ".ts", ".sh", ".md", ".json", ".yaml", ".yml"}
    return [f for f in p.rglob("*") if f.is_file() and f.suffix.lower() in exts]


# ── HTML 报告生成 ─────────────────────────────────────────────────────────────

def severity_to_class(severity):
    if "CRITICAL" in severity:
        return "critical"
    elif "WARNING" in severity:
        return "warning"
    return "info"


def render_issue_card(issue):
    """将单个 issue 渲染为 HTML 卡片"""
    e = html_mod.escape
    sev_class = severity_to_class(issue["severity"])
    loc = issue["file"]
    if issue.get("line"):
        loc = loc + ":" + str(issue["line"])
    snippet_html = ""
    if issue.get("snippet"):
        snippet_html = '<div class="snippet">' + e(issue["snippet"]) + "</div>"
    return (
        '<div class="issue-card ' + sev_class + '">'
        '<div class="issue-header">'
        '<span class="badge ' + sev_class + '">' + e(issue["severity"]) + "</span>"
        '<span class="rule-name">[' + e(issue["rule"]) + "]</span>"
        "</div>"
        '<div class="issue-loc">📁 ' + e(loc) + "</div>"
        '<div class="issue-msg">💬 ' + e(issue["message"]) + "</div>"
        + snippet_html +
        "</div>\n"
    )


def render_section(title, issues_list):
    if not issues_list:
        return ""
    cards = "".join(render_issue_card(i) for i in issues_list)
    return '<div class="section-title">' + title + "</div>\n" + cards


def generate_html_report(issues, target, mode):
    e = html_mod.escape
    critical = [i for i in issues if "CRITICAL" in i["severity"]]
    warning  = [i for i in issues if "WARNING" in i["severity"]]
    info     = [i for i in issues if "INFO" in i["severity"]]
    now_str  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    clean_msg = ""
    if not issues:
        clean_msg = '<div class="clean-msg">✅ 未发现问题！代码很干净哦～ 🐾</div>\n'

    body_sections = (
        clean_msg
        + render_section("🔴 Critical Issues", critical)
        + render_section("🟡 Warning Issues", warning)
        + render_section("🟢 Info", info)
    )

    css = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", sans-serif;
      background: #f0f2f5;
      color: #333;
      padding: 24px;
    }
    .container { max-width: 900px; margin: 0 auto; }
    .header-card {
      background: #1a237e;
      color: #fff;
      border-radius: 12px;
      padding: 28px 32px;
      margin-bottom: 20px;
      box-shadow: 0 4px 16px rgba(26,35,126,0.3);
    }
    .header-card h1 { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
    .header-card .meta { font-size: 13px; opacity: 0.8; margin-bottom: 18px; }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }
    .summary-item {
      background: rgba(255,255,255,0.15);
      border-radius: 8px;
      padding: 14px 18px;
      text-align: center;
    }
    .summary-item .count { font-size: 36px; font-weight: 800; line-height: 1; }
    .summary-item .label { font-size: 13px; opacity: 0.85; margin-top: 4px; }
    .summary-item.critical .count { color: #ff5252; }
    .summary-item.warning .count  { color: #ffd740; }
    .summary-item.info .count    { color: #69f0ae; }
    .section-title {
      font-size: 15px;
      font-weight: 600;
      color: #1a237e;
      margin: 20px 0 10px;
      padding-bottom: 6px;
      border-bottom: 2px solid #e3e6f0;
    }
    .issue-card {
      background: #fff;
      border-radius: 10px;
      padding: 16px 18px;
      margin-bottom: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
      border-left: 4px solid #e0e0e0;
    }
    .issue-card.critical { border-left-color: #f44336; }
    .issue-card.warning  { border-left-color: #ff9800; }
    .issue-card.info     { border-left-color: #4caf50; }
    .issue-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
    .badge {
      font-size: 12px;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 20px;
    }
    .badge.critical { background: #fde8e8; color: #c62828; }
    .badge.warning  { background: #fff3e0; color: #e65100; }
    .badge.info     { background: #e8f5e9; color: #2e7d32; }
    .rule-name { font-size: 12px; color: #888; font-family: monospace; }
    .issue-loc  { font-size: 12px; color: #555; margin-bottom: 5px; word-break: break-all; }
    .issue-msg  { font-size: 14px; color: #333; margin-bottom: 6px; }
    .snippet {
      font-size: 12px;
      font-family: "SFMono-Regular", Consolas, monospace;
      background: #f5f7fa;
      border-radius: 5px;
      padding: 6px 10px;
      color: #546e7a;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-all;
    }
    .clean-msg { text-align: center; color: #4caf50; font-size: 18px; padding: 40px; }
    .footer {
      text-align: center;
      font-size: 12px;
      color: #aaa;
      margin-top: 28px;
      padding-bottom: 10px;
    }
    """

    html_content = (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '  <meta charset="UTF-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "  <title>Code Audit Report — " + e(str(target)) + "</title>\n"
        "  <style>" + css + "  </style>\n"
        "</head>\n"
        "<body>\n"
        '  <div class="container">\n'
        '    <div class="header-card">\n'
        "      <h1>🔍 Code Audit Report</h1>\n"
        '      <div class="meta">Target: ' + e(str(target)) + " &nbsp;|&nbsp; Mode: " + e(mode) + " &nbsp;|&nbsp; Generated: " + now_str + "</div>\n"
        '      <div class="summary-grid">\n'
        '        <div class="summary-item critical"><div class="count">' + str(len(critical)) + '</div><div class="label">🔴 Critical</div></div>\n'
        '        <div class="summary-item warning"><div class="count">' + str(len(warning)) + '</div><div class="label">🟡 Warning</div></div>\n'
        '        <div class="summary-item info"><div class="count">' + str(len(info)) + '</div><div class="label">🟢 Info</div></div>\n'
        "      </div>\n"
        "    </div>\n"
        + body_sections +
        '    <div class="footer">OpenClaw code-audit Skill &nbsp;|&nbsp; 🐾 小爪</div>\n'
        "  </div>\n"
        "</body>\n"
        "</html>"
    )
    return html_content


# ── 终端报告打印 ──────────────────────────────────────────────────────────────

def print_report(issues, target):
    critical = [i for i in issues if "CRITICAL" in i["severity"]]
    warning  = [i for i in issues if "WARNING" in i["severity"]]
    info     = [i for i in issues if "INFO" in i["severity"]]

    print(f"\n{'='*60}")
    print(f"  🔍 Code Audit Report — {target}")
    print(f"{'='*60}")
    print(f"  🔴 Critical: {len(critical)}  🟡 Warning: {len(warning)}  🟢 Info: {len(info)}")
    print(f"{'='*60}\n")

    for issue in critical + warning + info:
        loc = f"{issue['file']}:{issue['line']}" if issue.get('line') else issue['file']
        print(f"{issue['severity']}  [{issue['rule']}]")
        print(f"  📁 {loc}")
        print(f"  💬 {issue['message']}")
        if issue.get('snippet'):
            print(f"  📝 {issue['snippet']}")
        print()

    if not issues:
        print("✅ 未发现问题！代码很干净哦～ 🐾\n")


# ── AI Prompt 生成 ────────────────────────────────────────────────────────────

def print_ai_prompt(issues, target):
    critical = [i for i in issues if "CRITICAL" in i["severity"]]
    warning  = [i for i in issues if "WARNING" in i["severity"]]
    key_issues = critical + warning

    if not key_issues:
        print("\n=== AI Analysis Prompt ===")
        print("[AI_PROMPT] 代码审计扫描完成，未发现 Critical 或 Warning 级别问题，代码状态良好。")
        print("=== End of AI Analysis Prompt ===\n")
        return

    lines = [
        "\n=== AI Analysis Prompt ===",
        f"[AI_PROMPT] 以下是 OpenClaw 代码审计扫描结果（目标：{target}）。",
        f"请对以下 {len(key_issues)} 个 Critical/Warning 问题逐一分析：",
        "  1. 风险等级是否准确？",
        "  2. 建议的修复方案是什么？",
        "  3. 是否有误报？如有，请说明原因。",
        "",
        "--- 问题列表 ---",
    ]
    for idx, issue in enumerate(key_issues, 1):
        loc = f"{issue['file']}:{issue['line']}" if issue.get('line') else issue['file']
        lines.append(f"\n#{idx} [{issue['severity']}] 规则: {issue['rule']}")
        lines.append(f"   位置: {loc}")
        lines.append(f"   描述: {issue['message']}")
        if issue.get("snippet"):
            lines.append(f"   代码: {issue['snippet']}")
    lines.append("\n--- End ---")
    lines.append("=== End of AI Analysis Prompt ===\n")

    print("\n".join(lines))


# ── 入口 ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="OpenClaw Code Audit Scanner")
    parser.add_argument("target", help="目标文件或目录路径")
    parser.add_argument("--mode", choices=["security", "quality", "soul", "all", "system"],
                        default="all", help="审计模式（默认: all）")
    parser.add_argument("--html", action="store_true",
                        help="生成 HTML 报告到桌面（~/Desktop）")
    parser.add_argument("--ai", action="store_true",
                        help="在末尾打印 AI Analysis Prompt 区块供 Claude 分析")
    args = parser.parse_args()

    # System 模式不需要扫描文件，直接运行系统检查
    if args.mode == "system":
        print(f"\n{'='*60}")
        print(f"  🛡️  System Security Audit — {args.target}")
        print(f"{'='*60}\n")
        all_issues = run_system_audit()
    else:
        files = collect_files(args.target)
        if not files:
            print(f"❌ 未找到可扫描的文件: {args.target}")
            sys.exit(1)

        all_issues = []
        for f in files:
            if is_soul_file(f) and args.mode in ("soul", "all"):
                all_issues.extend(scan_soul_file(f))
            elif not is_soul_file(f) and args.mode in ("security", "quality", "all"):
                all_issues.extend(scan_code_file(f, mode=args.mode))

        # Soul 模式额外扫描：Cron Job + Skill 触发词冲突
        if args.mode in ("soul", "all"):
            all_issues.extend(scan_cron_jobs(args.target))
            all_issues.extend(scan_skill_trigger_conflicts(args.target))

    # 终端报告
    print_report(all_issues, args.target)

    # HTML 报告
    if args.html:
        workspace_dir = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"code_audit_report_{timestamp}.html"
        html_path = workspace_dir / html_filename
        html_content = generate_html_report(all_issues, args.target, args.mode)
        html_path.write_text(html_content, encoding="utf-8")
        print(f"📄 HTML 报告已生成: {html_path}")

    # AI Prompt
    if args.ai:
        print_ai_prompt(all_issues, args.target)


if __name__ == "__main__":
    main()
