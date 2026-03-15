#!/usr/bin/env python3
"""
Skill Shield - OpenClaw 扩展安全管理系统
"""

import os
import re
import json
import glob
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
import argparse

# 配置
SKILLS_DIR = os.path.expanduser("~/.openclaw/workspace/skills")
MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
RISK_DB_PATH = os.path.join(MEMORY_DIR, "shield-risks.json")
CONFIG_PATH = os.path.join(SKILLS_DIR, "skill-shield", "config.json")

# 风险定义
RISK_DEFINITIONS = {
    "R001": {"name": "网络访问", "severity": "high", "keywords": ["requests", "curl", "fetch", "urllib", "http", "socket"]},
    "R002": {"name": "文件写入", "severity": "high", "keywords": ["write", "create", "save", "mkdir", "rmdir", "unlink"]},
    "R003": {"name": "文件读取", "severity": "medium", "keywords": ["read", "open", "cat", "glob", "listdir"]},
    "R004": {"name": "命令执行", "severity": "severe", "keywords": ["exec", "subprocess", "shell", "spawn", "Popen", "system"]},
    "R005": {"name": "外部API", "severity": "medium", "keywords": ["api", "webhook", "endpoint", "send", "notify", "post", "get"]},
    "R006": {"name": "数据外发", "severity": "severe", "keywords": ["upload", "send", "transfer", "export", "forward"]},
    "R007": {"name": "凭证访问", "severity": "severe", "keywords": ["apiKey", "password", "token", "secret", "credential", "auth"]},
    "R008": {"name": "无签名验证", "severity": "low", "keywords": []},
    "R009": {"name": "依赖未知", "severity": "medium", "keywords": ["requirements.txt", "package.json", "dependencies", "pip install"]},
    "R010": {"name": "权限过宽", "severity": "high", "keywords": ["chmod 777", "allowlist", "full"]},
}


class SkillShield:
    def __init__(self):
        self.skills_dir = SKILLS_DIR
        self.risk_db = self.load_risk_db()
        self.config = self.load_config()
        
    def load_risk_db(self) -> Dict:
        """加载风险数据库"""
        if os.path.exists(RISK_DB_PATH):
            try:
                with open(RISK_DB_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "version": "1.0.0",
            "lastScanTime": None,
            "skills": {},
            "allowlist": [],
            "history": []
        }
    
    def save_risk_db(self):
        """保存风险数据库"""
        os.makedirs(os.path.dirname(RISK_DB_PATH), exist_ok=True)
        with open(RISK_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.risk_db, f, ensure_ascii=False, indent=2)
    
    def load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "allowlist": [],
            "autoApprove": [],
            "blocked": [],
            "scanOnInstall": True,
            "promptOnHighRisk": True
        }
        
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except:
                pass
        return default_config
    
    def save_config(self):
        """保存配置文件"""
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_all_skills(self) -> List[str]:
        """获取所有已安装的 skills"""
        skills = []
        if os.path.exists(self.skills_dir):
            for item in os.listdir(self.skills_dir):
                item_path = os.path.join(self.skills_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    skills.append(item)
        return sorted(skills)
    
    def scan_skill(self, skill_name: str) -> Dict:
        """扫描单个 skill 的风险"""
        skill_path = os.path.join(self.skills_dir, skill_name)
        risks = set()
        
        if not os.path.exists(skill_path):
            return {"risks": [], "severity": "unknown", "error": "Skill not found"}
        
        # 扫描所有文件
        for root, dirs, files in os.walk(skill_path):
            # 跳过隐藏目录和特殊目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # 检测风险
                    for risk_id, risk_info in RISK_DEFINITIONS.items():
                        if not risk_info["keywords"]:
                            continue
                            
                        for keyword in risk_info["keywords"]:
                            if keyword.lower() in content.lower():
                                risks.add(risk_id)
                                break
                            
                except Exception:
                    pass
        
        # 检查是否有 _meta.json（来源验证）
        if not os.path.exists(os.path.join(skill_path, "_meta.json")):
            risks.add("R008")
        
        # 检查依赖文件
        if os.path.exists(os.path.join(skill_path, "requirements.txt")) or \
           os.path.exists(os.path.join(skill_path, "package.json")):
            risks.add("R009")
        
        # 计算严重程度
        severity = "low"
        if any(RISK_DEFINITIONS.get(r, {}).get("severity") == "severe" for r in risks):
            severity = "severe"
        elif any(RISK_DEFINITIONS.get(r, {}).get("severity") == "high" for r in risks):
            severity = "high"
        elif any(RISK_DEFINITIONS.get(r, {}).get("severity") == "medium" for r in risks):
            severity = "medium"
        
        return {
            "risks": sorted(list(risks)),
            "severity": severity,
            "path": skill_path,
            "scanTime": datetime.now().isoformat()
        }
    
    def scan_all_skills(self) -> Dict:
        """扫描所有 skills"""
        skills = self.get_all_skills()
        results = {}
        
        print(f"🔍 正在扫描 {len(skills)} 个 skills...\n")
        
        for skill in skills:
            # 检查是否在 allowlist
            if skill in self.config["allowlist"]:
                results[skill] = {
                    "status": "allowlisted",
                    "risks": [],
                    "severity": "trusted"
                }
                continue
            
            result = self.scan_skill(skill)
            results[skill] = result
            
            # 更新风险数据库
            self.risk_db["skills"][skill] = {
                "path": result.get("path"),
                "risks": result.get("risks", []),
                "severity": result.get("severity"),
                "scanTime": result.get("scanTime"),
                "userDecision": self.risk_db["skills"].get(skill, {}).get("userDecision", "pending")
            }
        
        self.risk_db["lastScanTime"] = datetime.now().isoformat()
        self.save_risk_db()
        
        return results
    
    def check_skill(self, skill_name: str) -> Dict:
        """检查单个 skill 的状态"""
        # 检查 allowlist
        if skill_name in self.config["allowlist"]:
            return {
                "status": "allowlisted",
                "trusted": True,
                "message": f"✅ {skill_name} 在 allowlist 中，默认信任"
            }
        
        # 检查 blocked
        if skill_name in self.config["blocked"]:
            return {
                "status": "blocked",
                "trusted": False,
                "message": f"🚫 {skill_name} 在黑名单中，已阻止"
            }
        
        # 检查风险数据库
        if skill_name in self.risk_db.get("skills", {}):
            skill_info = self.risk_db["skills"][skill_name]
            risks = skill_info.get("risks", [])
            severity = skill_info.get("severity", "unknown")
            
            return {
                "status": "scanned",
                "risks": risks,
                "severity": severity,
                "riskNames": [RISK_DEFINITIONS.get(r, {}).get("name", r) for r in risks],
                "message": f"⚠️ {skill_name} 风险等级: {severity}"
            }
        
        # 未扫描过
        return {
            "status": "unknown",
            "message": f"❓ {skill_name} 尚未扫描"
        }
    
    def check_and_prompt(self, skill_name: str) -> tuple[bool, str]:
        """
        检查 skill 风险并返回是否需要用户确认
        返回: (需要确认, 消息)
        """
        check_result = self.check_skill(skill_name)
        
        if check_result.get("trusted"):
            return False, check_result["message"]
        
        if check_result.get("status") == "blocked":
            return True, check_result["message"]
        
        severity = check_result.get("severity", "unknown")
        
        if severity in ["severe", "high"]:
            return True, f"""⚠️ 安全警告: {skill_name}
严重程度: {severity}
风险项:
{chr(10).join([f"  - {r}: {RISK_DEFINITIONS.get(r, {}).get('name', '未知风险')}" for r in check_result.get("risks", [])])}
是否继续执行? (yes/no)"""
        
        if severity == "medium" and self.config.get("promptOnHighRisk"):
            return True, f"""ℹ️ 风险提示: {skill_name}
风险等级: {severity}
风险项:
{chr(10).join([f"  - {r}: {RISK_DEFINITIONS.get(r, {}).get('name', '未知风险')}" for r in check_result.get("risks", [])])}
是否继续执行? (yes/no)"""
        
        return False, f"✅ {skill_name} 风险可控，继续执行"
    
    def add_to_allowlist(self, skill_name: str):
        """添加到 allowlist"""
        if skill_name not in self.config["allowlist"]:
            self.config["allowlist"].append(skill_name)
            self.save_config()
            
            # 更新风险数据库
            if skill_name in self.risk_db["skills"]:
                self.risk_db["skills"][skill_name]["userDecision"] = "approved"
                self.save_risk_db()
            
            return f"✅ 已将 {skill_name} 添加到 allowlist"
        return f"ℹ️ {skill_name} 已在 allowlist 中"
    
    def remove_from_allowlist(self, skill_name: str):
        """从 allowlist 移除"""
        if skill_name in self.config["allowlist"]:
            self.config["allowlist"].remove(skill_name)
            self.save_config()
            return f"✅ 已将 {skill_name} 从 allowlist 移除"
        return f"ℹ️ {skill_name} 不在 allowlist 中"
    
    def add_to_blocked(self, skill_name: str):
        """添加到黑名单"""
        if skill_name not in self.config["blocked"]:
            self.config["blocked"].append(skill_name)
            self.save_config()
            return f"🚫 已将 {skill_name} 添加到黑名单"
        return f"ℹ️ {skill_name} 已在黑名单中"
    
    def view_risks(self) -> str:
        """查看风险列表"""
        output = ["# 🎯 Skill 风险报告\n"]
        output.append(f"最后扫描时间: {self.risk_db.get('lastScanTime', '从未扫描')}\n")
        output.append(f"Allowlist: {', '.join(self.config['allowlist']) or '(空)'}\n")
        output.append(f"Blocked: {', '.join(self.config['blocked']) or '(空)'}\n")
        output.append("\n## 风险详情\n")
        
        for skill, info in self.risk_db.get("skills", {}).items():
            if skill in self.config["allowlist"]:
                continue
                
            severity = info.get("severity", "unknown")
            risks = info.get("risks", [])
            
            if severity == "severe":
                icon = "🔴"
            elif severity == "high":
                icon = "🟠"
            elif severity == "medium":
                icon = "🟡"
            else:
                icon = "🟢"
            
            output.append(f"### {icon} {skill} ({severity})\n")
            output.append(f"- 路径: {info.get('path', 'N/A')}\n")
            risk_str = ', '.join([f"{r}: {RISK_DEFINITIONS.get(r, {}).get('name', '未知')}" for r in risks]) or '无'
            output.append(f"- 风险: {risk_str}\n")
            output.append(f"- 用户决策: {info.get('userDecision', 'pending')}\n")
            output.append("\n")
        
        return "".join(output)
    
    def clear_risks(self):
        """清除风险记录"""
        self.risk_db = {
            "version": "1.0.0",
            "lastScanTime": None,
            "skills": {},
            "allowlist": self.config.get("allowlist", []),
            "history": []
        }
        self.save_risk_db()
        return "✅ 风险记录已清除"


def main():
    parser = argparse.ArgumentParser(description="Skill Shield - OpenClaw 扩展安全管理")
    parser.add_argument("action", nargs="?", choices=["scan", "check", "add-allowlist", "remove-allowlist", "add-blocked", "view", "clear"], 
                        help="操作类型")
    parser.add_argument("skill", nargs="?", help="Skill 名称")
    parser.add_argument("--force", "-f", action="store_true", help="强制执行")
    
    args = parser.parse_args()
    shield = SkillShield()
    
    if args.action == "scan" or (not args.action and not args.skill):
        results = shield.scan_all_skills()
        
        # 统计
        severe = sum(1 for r in results.values() if r.get("severity") == "severe")
        high = sum(1 for r in results.values() if r.get("severity") == "high")
        medium = sum(1 for r in results.values() if r.get("severity") == "medium")
        low = sum(1 for r in results.values() if r.get("severity") in ["low", "trusted"])
        
        print(f"\n📊 扫描完成!")
        print(f"   🔴 严重: {severe}")
        print(f"   🟠 高危: {high}")
        print(f"   🟡 中危: {medium}")
        print(f"   🟢 低危/安全: {low}")
        print(f"\n💾 风险报告已保存到: {RISK_DB_PATH}")
        
    elif args.action == "check":
        if not args.skill:
            print("错误: 请指定扩展名称")
            return
        
        result = shield.check_skill(args.skill)
        print(f"\n{result['message']}")
        
    elif args.action == "add-allowlist":
        if not args.skill:
            print("错误: 请指定扩展名称")
            return
        
        print(f"\n{shield.add_to_allowlist(args.skill)}")
        
    elif args.action == "remove-allowlist":
        if not args.skill:
            print("错误: 请指定扩展名称")
            return
        
        print(f"\n{shield.remove_from_allowlist(args.skill)}")
        
    elif args.action == "add-blocked":
        if not args.skill:
            print("错误: 请指定扩展名称")
            return
        
        print(f"\n{shield.add_to_blocked(args.skill)}")
        
    elif args.action == "view":
        print(f"\n{shield.view_risks()}")
        
    elif args.action == "clear":
        print(f"\n{shield.clear_risks()}")
        
    else:
        print("""
🎯 Skill Shield - 使用帮助

用法:
  python3 shield.py <action> [extension-name]

操作:
  scan                 扫描所有扩展的风险
  check <extension>   检查单个扩展的风险
  add-allowlist <extension>  添加扩展到 allowlist
  remove-allowlist <extension> 从 allowlist 移除
  add-blocked <extension>  添加到黑名单
  view                查看风险列表
  clear               清除风险记录

示例:
  python3 shield.py scan
  python3 shield.py check weather-search
  python3 shield.py add-allowlist file-search
  python3 shield.py view
""")


if __name__ == "__main__":
    main()