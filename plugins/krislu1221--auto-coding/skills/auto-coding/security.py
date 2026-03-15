"""
安全配置 - 自主编码 Agent 安全沙箱
Security Configuration for Autonomous Coding Agent
"""

import shlex
import re
from typing import Tuple, List, Dict, Any


# =============================================================================
# 命令白名单 (参考 Claude Quickstarts)
# =============================================================================

# 允许的命令集合
ALLOWED_COMMANDS = {
    # 文件检查
    "ls", "cat", "head", "tail", "wc", "grep", "find", "tree",
    # 文件操作
    "cp", "mkdir", "chmod", "touch", "mv", "rm", "rmdir",
    # 目录
    "pwd", "cd",
    # Node.js
    "npm", "npx", "node", "yarn", "pnpm",
    # Python
    "pip", "pip3", "python", "python3", "pytest", "unittest", "poetry",
    # 版本控制
    "git",
    # 进程管理
    "ps", "lsof", "sleep", "pkill", "kill", "pgrep",
    # 构建工具
    "make", "cmake", "webpack", "vite", "rollup", "tsc",
    # 系统信息
    "uname", "whoami", "echo", "date", "time",
    # 网络 (谨慎使用)
    "curl", "wget",
    # 文本编辑
    "sed", "awk",
}

# 需要额外验证的命令
COMMANDS_NEEDING_EXTRA_VALIDATION = {
    "pkill": {
        "allowed_targets": {"node", "npm", "npx", "python", "python3", "vite", "next", "webpack"},
        "description": "只允许杀死开发进程"
    },
    "kill": {
        "allowed_targets": {"node", "npm", "npx", "python", "python3", "vite", "next", "webpack"},
        "description": "只允许杀死开发进程"
    },
    "chmod": {
        "allowed_modes": {"+x", "u+x", "g+x", "o+x", "a+x", "-x"},
        "description": "只允许修改执行权限"
    },
    "rm": {
        "blocked_patterns": ["-rf", "-fr", "--force -recursive"],
        "description": "禁止强制递归删除"
    },
    "curl": {
        "blocked_patterns": ["-o", "--output", "|", ">", ">>"],
        "description": "禁止直接写入文件"
    },
    "wget": {
        "blocked_patterns": ["-O", "--output-document", "|", ">", ">>"],
        "description": "禁止直接写入文件"
    },
}

# 完全禁止的命令
BLOCKED_COMMANDS = {
    "sudo": "禁止提权操作",
    "su": "禁止切换用户",
    "dd": "禁止底层磁盘操作",
    "mkfs": "禁止格式化操作",
    "fdisk": "禁止分区操作",
    "mount": "禁止挂载操作",
    "umount": "禁止卸载操作",
    "iptables": "禁止防火墙配置",
    "ufw": "禁止防火墙配置",
    "systemctl": "禁止系统服务管理",
    "service": "禁止系统服务管理",
    "crontab": "禁止定时任务配置",
    "passwd": "禁止密码修改",
    "useradd": "禁止用户管理",
    "userdel": "禁止用户管理",
    "usermod": "禁止用户管理",
    "visudo": "禁止 sudo 配置",
}


# =============================================================================
# 命令验证函数
# =============================================================================

def split_command_segments(command_string: str) -> List[str]:
    """
    分割复合命令为独立命令段
    处理 && || ; 但不处理管道 (管道视为单个命令)
    """
    segments = re.split(r'\s*(?:&&|\|\|)\s*', command_string)
    result = []
    for segment in segments:
        sub_segments = re.split(r'(?<!["\'])\s*;\s*(?!["\'])', segment)
        for sub in sub_segments:
            sub = sub.strip()
            if sub:
                result.append(sub)
    return result


def extract_commands(command_string: str) -> List[str]:
    """
    从 shell 命令字符串中提取命令名称
    处理管道、命令链和子 shell
    """
    commands = []
    segments = re.split(r'(?<!["\'])\s*;\s*(?!["\'])', command_string)
    
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        
        try:
            tokens = shlex.split(segment)
        except ValueError:
            # 格式错误，返回空列表 (安全失败)
            return []
        
        if not tokens:
            continue
        
        expect_command = True
        
        for token in tokens:
            if token in ("|", "||", "&&", "&"):
                expect_command = True
                continue
            
            if token in ("if", "then", "else", "elif", "fi", "for", "while", 
                        "until", "do", "done", "case", "esac", "in", "!", 
                        "{", "}", "(", ")"):
                continue
            
            if token.startswith("-"):
                continue
            
            if "=" in token and not token.startswith("="):
                continue
            
            if expect_command:
                cmd = token.split("/")[-1]  # 处理路径
                commands.append(cmd)
                expect_command = False
    
    return commands


def validate_pkill_command(command_string: str) -> Tuple[bool, str]:
    """验证 pkill/kill 命令"""
    config = COMMANDS_NEEDING_EXTRA_VALIDATION.get("pkill")
    allowed_process_names = config["allowed_targets"]
    
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "无法解析 pkill 命令"
    
    if not tokens:
        return False, "空命令"
    
    args = []
    for token in tokens[1:]:
        if not token.startswith("-"):
            args.append(token)
    
    if not args:
        return False, "pkill 需要进程名称"
    
    target = args[-1]
    
    if " " in target:
        target = target.split()[0]
    
    if target in allowed_process_names:
        return True, ""
    return False, f"pkill 只允许用于开发进程：{allowed_process_names}"


def validate_chmod_command(command_string: str) -> Tuple[bool, str]:
    """验证 chmod 命令"""
    config = COMMANDS_NEEDING_EXTRA_VALIDATION.get("chmod")
    allowed_modes = config["allowed_modes"]
    
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "无法解析 chmod 命令"
    
    if not tokens or tokens[0] != "chmod":
        return False, "不是 chmod 命令"
    
    mode = None
    files = []
    
    for token in tokens[1:]:
        if token.startswith("-"):
            return False, "chmod 不支持标志"
        elif mode is None:
            mode = token
        else:
            files.append(token)
    
    if mode is None:
        return False, "chmod 需要模式参数"
    
    if not files:
        return False, "chmod 需要文件参数"
    
    if mode not in allowed_modes:
        return False, f"chmod 只允许模式：{allowed_modes}"
    
    return True, ""


def validate_rm_command(command_string: str) -> Tuple[bool, str]:
    """验证 rm 命令"""
    config = COMMANDS_NEEDING_EXTRA_VALIDATION.get("rm")
    blocked_patterns = config["blocked_patterns"]
    
    for pattern in blocked_patterns:
        if pattern in command_string:
            return False, f"rm 禁止使用模式：{pattern}"
    
    return True, ""


def validate_curl_command(command_string: str) -> Tuple[bool, str]:
    """验证 curl 命令"""
    config = COMMANDS_NEEDING_EXTRA_VALIDATION.get("curl")
    blocked_patterns = config["blocked_patterns"]
    
    for pattern in blocked_patterns:
        if pattern in command_string:
            return False, f"curl 禁止使用模式：{pattern}"
    
    return True, ""


def validate_wget_command(command_string: str) -> Tuple[bool, str]:
    """验证 wget 命令"""
    config = COMMANDS_NEEDING_EXTRA_VALIDATION.get("wget")
    blocked_patterns = config["blocked_patterns"]
    
    for pattern in blocked_patterns:
        if pattern in command_string:
            return False, f"wget 禁止使用模式：{pattern}"
    
    return True, ""


async def validate_command(command: str) -> Tuple[bool, str]:
    """
    验证命令是否允许
    
    Returns:
        (is_allowed, reason_if_blocked)
    """
    if not command or not command.strip():
        return False, "空命令"
    
    # 检查完全禁止的命令
    commands = extract_commands(command)
    if not commands:
        return False, "无法解析命令"
    
    for cmd in commands:
        if cmd in BLOCKED_COMMANDS:
            return False, f"禁止的命令 '{cmd}': {BLOCKED_COMMANDS[cmd]}"
    
    # 白名单检查
    for cmd in commands:
        if cmd not in ALLOWED_COMMANDS:
            return False, f"命令 '{cmd}' 不在白名单中"
    
    # 分割命令段进行额外验证
    segments = split_command_segments(command)
    
    # 额外验证敏感命令
    for cmd in commands:
        if cmd in COMMANDS_NEEDING_EXTRA_VALIDATION:
            cmd_segment = command  # 简化处理，使用完整命令
            
            if cmd in ("pkill", "kill"):
                allowed, reason = validate_pkill_command(cmd_segment)
                if not allowed:
                    return False, reason
            elif cmd == "chmod":
                allowed, reason = validate_chmod_command(cmd_segment)
                if not allowed:
                    return False, reason
            elif cmd == "rm":
                allowed, reason = validate_rm_command(cmd_segment)
                if not allowed:
                    return False, reason
            elif cmd == "curl":
                allowed, reason = validate_curl_command(cmd_segment)
                if not allowed:
                    return False, reason
            elif cmd == "wget":
                allowed, reason = validate_wget_command(cmd_segment)
                if not allowed:
                    return False, reason
    
    return True, ""


def get_security_report() -> Dict[str, Any]:
    """获取安全配置报告"""
    return {
        "allowed_commands_count": len(ALLOWED_COMMANDS),
        "blocked_commands_count": len(BLOCKED_COMMANDS),
        "extra_validation_count": len(COMMANDS_NEEDING_EXTRA_VALIDATION),
        "allowed_commands": sorted(list(ALLOWED_COMMANDS)),
        "blocked_commands": {k: v for k, v in BLOCKED_COMMANDS.items()},
    }


# =============================================================================
# 测试代码
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    print("运行 Security 测试...\n")
    
    async def run_tests():
        test_cases = [
            # (command, should_allow, description)
            ("ls -la", True, "基本文件查看"),
            ("cat file.txt", True, "读取文件"),
            ("git status", True, "Git 操作"),
            ("npm install", True, "NPM 安装"),
            ("python3 app.py", True, "Python 运行"),
            ("mkdir test", True, "创建目录"),
            ("chmod +x script.sh", True, "添加执行权限"),
            ("pkill node", True, "杀死 node 进程"),
            
            ("sudo rm -rf /", False, "提权删除"),
            ("rm -rf /", False, "递归强制删除"),
            ("pkill sshd", False, "杀死非开发进程"),
            ("dd if=/dev/zero", False, "磁盘操作"),
            ("mkfs.ext4 /dev/sda", False, "格式化"),
            ("unknown_command", False, "未知命令"),
            ("curl http://example.com -o file.txt", False, "curl 写入文件"),
        ]
        
        passed = 0
        failed = 0
        
        for command, should_allow, description in test_cases:
            allowed, reason = await validate_command(command)
            
            if allowed == should_allow:
                print(f"✅ {description}: {command}")
                passed += 1
            else:
                print(f"❌ {description}: {command}")
                print(f"   期望：{'允许' if should_allow else '禁止'}, 实际：{'允许' if allowed else '禁止'}")
                if reason:
                    print(f"   原因：{reason}")
                failed += 1
        
        print(f"\n{'='*50}")
        print(f"通过：{passed}/{len(test_cases)}")
        print(f"失败：{failed}/{len(test_cases)}")
        
        if failed == 0:
            print("\n🎉 所有 Security 测试通过!")
        else:
            print(f"\n⚠️  有 {failed} 个测试失败")
        
        return failed == 0
    
    # 运行测试
    success = asyncio.run(run_tests())
    exit(0 if success else 1)
