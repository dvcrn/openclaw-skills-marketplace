#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import platform
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

# ------------------------------------------------------------------
# 基礎檢查器
# ------------------------------------------------------------------
class BaseChecker:
    def __init__(self):
        self.results = {}
        self.issues = []
        self.recommendations = []

    def check(self) -> Dict[str, Any]:
        raise NotImplementedError("子類必須實作此方法")

    def get_issues(self) -> List[str]:
        return self.issues

    def get_recommendations(self) -> List[str]:
        return self.recommendations


# ------------------------------------------------------------------
# 系統工具檢查器（Python、pip、git、docker、jq、powershell、node）
# ------------------------------------------------------------------
class SystemToolChecker(BaseChecker):
    def __init__(self):
        super().__init__()
        self.tools = {
            "python": {"commands": ["python", "python3"], "version_flag": "--version", "required": True},
            "pip": {"commands": ["pip", "pip3"], "version_flag": "--version", "required": True},
            "git": {"commands": ["git"], "version_flag": "--version", "required": False},
            "docker": {"commands": ["docker"], "version_flag": "--version", "required": False},
            "jq": {"commands": ["jq"], "version_flag": "--version", "required": False},
            "powershell": {"commands": ["pwsh", "powershell.exe", "powershell"], "version_flag": "-v", "required": False},
            "node": {"commands": ["node", "nodejs"], "version_flag": "--version", "required": False},
        }

    def check_tool(self, name: str, info: Dict) -> Dict:
        result = {"installed": False, "version": "未知", "path": ""}

        for cmd in info["commands"]:
            try:
                output = subprocess.run([cmd, info["version_flag"]],
                                       capture_output=True,
                                       text=True,
                                       timeout=5)
                if output.returncode == 0:
                    result["installed"] = True
                    result["version"] = output.stdout.strip()
                    # 找到可執行檔路徑（Windows 之間用 where，Linux 之間用 which）
                    which_cmd = "where" if platform.system() == "Windows" else "which"
                    path_out = subprocess.run([which_cmd, cmd],
                                              capture_output=True,
                                              text=True,
                                              timeout=3)
                    if path_out.returncode == 0:
                        result["path"] = path_out.stdout.strip()
                    break
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        if not result["installed"] and info["required"]:
            self.issues.append(f"{name} 未安裝")
            self.recommendations.append(f"安裝 {name}")

        return result

    def check(self) -> Dict[str, Any]:
        self.results = {}
        for name, info in self.tools.items():
            self.results[name] = self.check_tool(name, info)
        return self.results


# ------------------------------------------------------------------
# Python 套件檢查器
# ------------------------------------------------------------------
class PythonPackageChecker(BaseChecker):
    def __init__(self):
        super().__init__()
        self.packages = {
            "語音處理": ["vosk", "sounddevice", "pyaudio", "pyttsx3", "pydub", "SpeechRecognition"],
            "資料處理": ["numpy", "pandas", "scipy", "scikit-learn"],
            "深度學習": ["torch", "tensorflow", "keras", "transformers"],
            "RAG相關": ["langchain", "chromadb", "sentence-transformers", "openai", "llama-index", "faiss-cpu"],
            "工具類": ["tqdm", "opencc", "requests", "python-dotenv", "yt-dlp"],
        }
        self.mapping = {
            "sentence-transformers": "sentence_transformers",
            "faiss-cpu": "faiss",
            "llama-index": "llama_index",
        }

    def check_pkg(self, pkg: str) -> Dict:
        import_name = self.mapping.get(pkg, pkg)
        res = {"installed": False, "version": "未知", "import_name": import_name}
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is not None:
                res["installed"] = True
                try:
                    if sys.version_info >= (3, 8):
                        from importlib.metadata import version
                        res["version"] = version(pkg)
                    else:
                        raise ImportError
                except Exception:
                    res["version"] = "未知"
        except ImportError:
            pass

        if not res["installed"]:
            self.issues.append(f"Python 套件 {pkg} 未安裝")
            self.recommendations.append(f"安裝 Python 套件: pip install {self.mapping.get(pkg, pkg)}")

        return res

    def check(self) -> Dict[str, Any]:
        self.results = {}
        for cat, pkgs in self.packages.items():
            self.results[cat] = {}
            for pk in pkgs:
                self.results[cat][pk] = self.check_pkg(pk)
        return self.results


# ------------------------------------------------------------------
# 工作區檢查器
# ------------------------------------------------------------------
class WorkspaceChecker(BaseChecker):
    def __init__(self, path: Optional[str] = None):
        super().__init__()
        self.ws = Path(path) if path else Path.cwd()

    def check(self) -> Dict[str, Any]:
        self.results = {
            "exists": self.ws.exists(),
            "is_dir": self.ws.is_dir() if self.ws.exists() else False,
            "items": [],
        }
        common_items = [
            "model",
            "utils",
            "scripts",
            "output",
            "data",
            "requirements.txt",
            "config.json",
            "Dockerfile",
            "docker-compose.yml",
        ]

        if self.results["exists"] and self.results["is_dir"]:
            for name in common_items:
                p = self.ws / name
                self.results["items"].append(
                    {"name": name, "exists": p.exists(), "is_dir": p.is_dir() if p.exists() else False}
                )
                if not p.exists():
                    self.issues.append(f"工作區缺少 {name}")
        else:
            self.issues.append("工作區不存在或不是目錄")

        return self.results


# ------------------------------------------------------------------
# Docker 檢查器
# ------------------------------------------------------------------
class DockerChecker(BaseChecker):
    def check(self) -> Dict[str, Any]:
        self.results = {
            "docker_installed": False,
            "docker_compose_installed": False,
            "docker_running": False,
            "containers": [],
        }

        try:
            p = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
            self.results["docker_installed"] = p.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        try:
            p = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True, timeout=5)
            self.results["docker_compose_installed"] = p.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        if self.results["docker_installed"]:
            try:
                p = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
                self.results["docker_running"] = p.returncode == 0
            except Exception:
                pass

        if self.results["docker_running"]:
            try:
                p = subprocess.run(
                    ["docker", "ps", "--format", "{{.Names}}|{{.Image}}|{{.Status}}"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if p.returncode == 0:
                    for line in p.stdout.strip().splitlines():
                        if line:
                            name, image, status = line.split("|")
                            self.results["containers"].append(
                                {"name": name, "image": image, "status": status}
                            )
            except Exception:
                pass

        if not self.results["docker_installed"]:
            self.issues.append("Docker 未安裝")
            self.recommendations.append("安裝 Docker Desktop")

        return self.results


# ------------------------------------------------------------------
# RAG 環境檢查器（示例：API KEY 設定）
# ------------------------------------------------------------------
class RAGChecker(BaseChecker):
    def check(self) -> Dict[str, Any]:
        self.results = {"vector_databases": [], "llm_providers": []}

        providers = [
            {"name": "OpenAI", "env": "OPENAI_API_KEY"},
            {"name": "Anthropic", "env": "ANTHROPIC_API_KEY"},
            {"name": "Cohere", "env": "COHERE_API_KEY"},
            {"name": "HuggingFace", "env": "HUGGINGFACE_API_KEY"},
            {"name": "Azure OpenAI", "env": "AZURE_OPENAI_API_KEY"},
        ]

        cnt = 0
        for p in providers:
            key = os.getenv(p["env"])
            conf = bool(key and key != "")
            self.results["llm_providers"].append({"name": p["name"], "env": p["env"], "configured": conf})
            if conf:
                cnt += 1
            else:
                self.issues.append(f"{p['name']} API KEY 未設定")
                self.recommendations.append(f"設定環境變量 {p['env']}")

        if cnt == 0:
            self.issues.append("未設定任何 LLM 供應商 API KEY")
            self.recommendations.append("至少設定一個 LLM API KEY")

        return self.results


# ------------------------------------------------------------------
# 總體環境檢測 API（核心邏輯）
# ------------------------------------------------------------------
class EnvironmentCheckAPI:
    def __init__(self, ws: Optional[str] = None):
        self.ws = ws if ws else str(Path.cwd())
        self.checkers = {
            "system_tools": SystemToolChecker(),
            "python_packages": PythonPackageChecker(),
            "workspace": WorkspaceChecker(self.ws),
            "docker": DockerChecker(),
            "rag_environment": RAGChecker(),
        }
        self.results = {}
        self.all_issues = []
        self.all_recs = []

    # 讀取「已安裝記錄檔」(JSON)
    def load_install_record(self, file: str) -> Dict[str, str]:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            print(f"[ERROR] 無法讀取安裝記錄 {file}: {e}")
            return {}

    # 針對缺失項目產生安裝指令
    def recommend_install(self, missing: List[Dict]) -> List[str]:
        cmds = []
        for item in missing:
            name = item["name"]
            if name == "git":
                cmds.append("winget install -e --id Git.Git")
            elif name == "powershell":
                cmds.append("winget install -e --id Microsoft.PowerShell")
            elif name == "docker":
                cmds.append("winget install -e --id Docker.DockerDesktop")
            elif name == "jq":
                cmds.append("winget install -e --id jqlang.jq")
            elif name == "node":
                cmds.append("winget install -e --id OpenJS.NodeJS")
            elif name == "python":
                cmds.append("winget install -e --id Python.Python.3")
            else:
                cmds.append(f"# 未知工具 {name}，請自行搜尋安裝指令")
        return cmds

    # 安裝Python包
    def install_python_packages(self, packages: List[str]) -> List[str]:
        """安装Python包并返回安装结果"""
        results = []
        for pkg in packages:
            try:
                print(f"正在安装 {pkg}...")
                result = subprocess.run([sys.executable, "-m", "pip", "install", pkg], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    results.append(f"✓ 成功安装 {pkg}")
                    print(f"✓ 成功安装 {pkg}")
                else:
                    results.append(f"✗ 安装失败 {pkg}: {result.stderr[-200:]}")  # 只显示最后200个字符的错误
                    print(f"✗ 安装失败 {pkg}: {result.stderr[-200:]}")
            except subprocess.TimeoutExpired:
                results.append(f"✗ 安装超时 {pkg}")
                print(f"✗ 安装超时 {pkg}")
        return results

    # 主要執行檢查
    def run_checks(self, types: Optional[List[str]] = None) -> Dict[str, Any]:
        if types is None:
            types = list(self.checkers.keys())
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system": platform.system(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "checks": {},
            "issues": [],
            "recommendations": [],
            "environment_ready": True,
        }

        for name, checker in self.checkers.items():
            self.results["checks"][name] = checker.check()
            self.all_issues.extend(checker.get_issues())
            self.all_recs.extend(checker.get_recommendations())

        self.results["issues"] = self.all_issues
        self.results["recommendations"] = self.all_recs
        if self.all_issues:
            self.results["environment_ready"] = False

        return self.results

    # 把報告寫進 JSON
    def save_report(self, path: str = "environment_report.json") -> str:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        return path

    # -----------------------------
    # 由安裝記錄修復功能
    # -----------------------------
    def restore_from_record(self, record_file: str) -> Tuple[List[Dict], List[str]]:
        # 先跑一次標準檢查
        self.run_checks()

        installed = self.load_install_record(record_file)

        missing = []
        # 只比較 "system_tools" 的工具
        for name, info in self.results["checks"]["system_tools"].items():
            if not info["installed"]:
                # 若 record 裡有同名且版本相同，就不算缺失
                rec_ver = installed.get(name)
                if rec_ver and rec_ver == info["version"]:
                    continue
                missing.append(
                    {"name": name, "current": info["version"], "recorded": rec_ver}
                )

        cmds = self.recommend_install(missing)
        return missing, cmds

    # -----------------------------
    # 自動安裝缺失的Python包
    # -----------------------------
    def auto_install_packages(self) -> List[str]:
        """自动安装所有缺失的Python包"""
        # 先运行检查获取所有缺失的包
        self.run_checks()
        
        # 从recommendations中提取需要安装的包
        packages_to_install = []
        for recommendation in self.all_recs:
            if recommendation.startswith("安裝 Python 套件: pip install "):
                pkg = recommendation.replace("安裝 Python 套件: pip install ", "").strip()
                packages_to_install.append(pkg)
        
        if not packages_to_install:
            print("没有需要安装的Python包")
            return ["没有需要安装的Python包"]
            
        print(f"开始安装 {len(packages_to_install)} 个Python包...")
        results = self.install_python_packages(packages_to_install)
        print("Python包安装完成！")
        return results


# ------------------------------------------------------------------
# 指令列入口
# ------------------------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="MECT – 模块化環境檢查工具（帶自動修復功能）"
    )
    parser.add_argument("--workspace", "-w", help="工作區路徑（默認是當前目錄）")
    parser.add_argument("--output", "-o", help="輸出報告檔名（默認 environment_report.json）")
    parser.add_argument(
        "--check",
        "-c",
        nargs="+",
        choices=[
            "system_tools",
            "python_packages",
            "workspace",
            "docker",
            "rag_environment",
        ],
        help="指明要執行的檢查類別",
    )
    parser.add_argument("--json", "-j", action="store_true", help="只輸出原始 JSON")
    parser.add_argument(
        "--restore-file",
        "-r",
        type=str,
        help="指定安裝記錄檔，產生缺失安裝指令（winget 風格）",
    )
    parser.add_argument(
        "--install-missing",
        "-i",
        action="store_true",
        help="自動安裝所有缺失的Python包",
    )

    args = parser.parse_args()

    api = EnvironmentCheckAPI(args.workspace)

    if args.install_missing:
        print("開始自動安裝缺失的Python包...")
        results = api.auto_install_packages()
        print("\n安裝結果摘要:")
        for result in results:
            print(result)
    else:
        res = api.run_checks(args.check)

        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("\n---- 環境檢查結果 ----")
            print(json.dumps(res, indent=2, ensure_ascii=False))
            print("────────────────────────────\n")

        out_path = args.output if args.output else "environment_report.json"
        api.save_report(out_path)
        print(f"\n📄 報告已寫入: {out_path}")

        # -------------------------------------
        # 若有 --restore-file，列出需要安裝的指令
        # -------------------------------------
        if args.restore_file:
            missing, commands = api.restore_from_record(args.restore_file)
            print("\n---- 需要安裝的項目 ----")
            if not missing:
                print("已全部安裝完畢，無需額外操作。")
            else:
                for m in missing:
                    print(f"{m['name']} – 目前: {m['current']}  →  錄錄: {m.get('recorded','未知')}")
                print("\n建議執行的安裝指令 (複製回 Windows CMD/PS 直接執行即可)：")
                for cmd in commands:
                    print(cmd)


if __name__ == "__main__":
    main()