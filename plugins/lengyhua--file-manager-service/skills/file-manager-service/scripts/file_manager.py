#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Manager Service Client - 文件管理服务客户端
用于调用运行在 8888 端口的文件管理服务 API
包含服务启动、关闭、状态检查功能
"""

import requests
import json
import sys
import subprocess
import os
import time
import socket
from typing import Optional
from pathlib import Path

BASE_URL = "http://127.0.0.1:8888"
SERVICE_DIR = Path(__file__).parent.parent / "file-manager-service"
PID_FILE = Path(__file__).parent / ".service.pid"
LOG_FILE = Path(__file__).parent / ".service.log"


def api_request(method: str, endpoint: str, params: dict = None, json_data: dict = None) -> dict:
    """发送 API 请求"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, params=params, timeout=30)
        elif method == "POST":
            resp = requests.post(url, json=json_data, timeout=30)
        else:
            return {"error": f"不支持的方法：{method}"}
        
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": "无法连接到文件管理服务，请确认服务正在运行 (http://127.0.0.1:8888)"}
    except requests.exceptions.Timeout:
        return {"error": "请求超时"}
    except Exception as e:
        return {"error": str(e)}


def list_files(path: str = "") -> dict:
    """列出指定路径的文件和目录"""
    params = {"path": path} if path else {}
    return api_request("GET", "/api/files", params=params)


def get_file_content(path: str) -> dict:
    """获取文件内容"""
    return api_request("GET", "/api/file/content", params={"path": path})


def save_file(path: str, content: str) -> dict:
    """保存文件内容"""
    return api_request("POST", "/api/file/save", json_data={"path": path, "content": content})


def download_file(path: str, save_path: str = None) -> dict:
    """下载文件"""
    url = f"{BASE_URL}/api/file/download"
    try:
        resp = requests.get(url, params={"path": path}, timeout=30)
        resp.raise_for_status()
        
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(resp.content)
            return {"success": True, "message": f"文件已下载到：{save_path}", "size": len(resp.content)}
        else:
            return {"success": True, "content": resp.content, "size": len(resp.content)}
    except Exception as e:
        return {"error": str(e)}


def delete_item(path: str) -> dict:
    """删除文件或目录"""
    return api_request("POST", "/api/delete", json_data={"path": path})


def create_directory(path: str, name: str) -> dict:
    """创建目录"""
    return api_request("POST", "/api/create/dir", json_data={"path": path, "name": name})


def create_file(path: str, name: str, content: str = "") -> dict:
    """创建文件"""
    return api_request("POST", "/api/create/file", json_data={"path": path, "name": name, "content": content})


def search_files(query: str) -> dict:
    """搜索文件"""
    return api_request("GET", "/api/search", params={"q": query})


def get_stats() -> dict:
    """获取统计信息"""
    return api_request("GET", "/api/stats")


def get_note(path: str) -> dict:
    """获取目录备注"""
    return api_request("GET", "/api/notes/get", params={"path": path})


def save_note(path: str, note: str) -> dict:
    """保存目录备注"""
    return api_request("POST", "/api/notes/save", json_data={"path": path, "note": note})


def move_item(source: str, dest: str) -> dict:
    """移动文件或目录"""
    return api_request("POST", "/api/move", json_data={"source": source, "dest": dest})


def download_item(path: str, save_path: str = None) -> dict:
    """下载文件或目录"""
    url = f"{BASE_URL}/api/download"
    try:
        resp = requests.get(url, params={"path": path}, timeout=60, stream=True)
        resp.raise_for_status()
        
        # 获取文件名
        content_disposition = resp.headers.get('Content-Disposition', '')
        filename = path.split('/')[-1]
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip()
        
        target_path = save_path or filename
        
        # 保存到文件
        total_size = int(resp.headers.get('Content-Length', 0))
        downloaded = 0
        
        with open(target_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    print(f"\r下载进度：{progress:.1f}%", end='', flush=True)
        
        print()  # 换行
        return {"success": True, "message": f"已下载到：{target_path}", "size": downloaded}
    except Exception as e:
        return {"error": str(e)}


def get_tree(path: str = "") -> dict:
    """获取目录树结构"""
    return api_request("GET", "/api/tree", params={"path": path})


def is_port_in_use(port: int) -> bool:
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def get_service_pid() -> int:
    """获取服务进程 ID"""
    if PID_FILE.exists():
        try:
            return int(PID_FILE.read_text().strip())
        except:
            pass
    return 0


def is_service_running() -> bool:
    """检查服务是否正在运行"""
    pid = get_service_pid()
    if pid:
        try:
            os.kill(pid, 0)
            return is_port_in_use(8888)
        except ProcessLookupError:
            PID_FILE.unlink(missing_ok=True)
    return is_port_in_use(8888)


def start_service() -> dict:
    """启动服务"""
    if is_service_running():
        pid = get_service_pid()
        return {"success": False, "message": f"服务已在运行 (PID: {pid})"}
    
    if not SERVICE_DIR.exists():
        return {"success": False, "message": f"服务目录不存在：{SERVICE_DIR}"}
    
    app_file = SERVICE_DIR / "app.py"
    if not app_file.exists():
        return {"success": False, "message": f"找不到 app.py"}
    
    try:
        # 后台启动服务
        with open(LOG_FILE, 'w') as log:
            proc = subprocess.Popen(
                [sys.executable, str(app_file)],
                stdout=log,
                stderr=log,
                cwd=str(SERVICE_DIR),
                start_new_session=True
            )
        
        PID_FILE.write_text(str(proc.pid))
        
        # 等待服务启动
        for _ in range(30):
            time.sleep(0.5)
            if is_port_in_use(8888):
                return {
                    "success": True,
                    "message": f"服务已启动 (PID: {proc.pid})",
                    "url": "http://127.0.0.1:8888",
                    "pid": proc.pid
                }
        
        return {"success": False, "message": "服务启动超时，请检查日志", "log": str(LOG_FILE)}
    except Exception as e:
        return {"success": False, "message": f"启动失败：{str(e)}"}


def find_service_pid_by_port(port: int) -> int:
    """通过端口查找进程 PID（遍历/proc）"""
    import glob
    for fd_path in glob.glob('/proc/*/fd/*'):
        try:
            if os.path.islink(fd_path) and f'socket:' in os.readlink(fd_path):
                pid = int(fd_path.split('/')[2])
                try:
                    with open(f'/proc/{pid}/cmdline', 'r') as f:
                        cmdline = f.read()
                        if 'python' in cmdline and ('app.py' in cmdline or 'flask' in cmdline.lower()):
                            try:
                                with open(f'/proc/{pid}/net/tcp', 'r') as netf:
                                    for line in netf:
                                        parts = line.split()
                                        if len(parts) > 1:
                                            local_addr = parts[1]
                                            port_hex = local_addr.split(':')[1]
                                            if int(port_hex, 16) == port:
                                                return pid
                            except:
                                pass
                except:
                    pass
        except:
            pass
    return 0


def stop_service() -> dict:
    """停止服务"""
    pid = get_service_pid()
    
    if not pid and not is_port_in_use(8888):
        return {"success": True, "message": "服务未运行"}
    
    try:
        # 优先使用 PID 文件
        if pid:
            try:
                os.kill(pid, 9)
            except ProcessLookupError:
                pass
            # 尝试杀死整个进程组
            try:
                os.killpg(pid, 9)
            except:
                pass
        else:
            # 通过端口查找 PID
            pid = find_service_pid_by_port(8888)
            if pid:
                try:
                    os.kill(pid, 9)
                except:
                    pass
        
        PID_FILE.unlink(missing_ok=True)
        time.sleep(0.5)
        
        if is_port_in_use(8888):
            return {"success": False, "message": "服务仍在运行，请手动停止 (kill -9 $(lsof -ti:8888))"}
        
        return {"success": True, "message": "服务已停止"}
    except Exception as e:
        return {"success": False, "message": f"停止失败：{str(e)}"}


def service_status() -> dict:
    """获取服务状态"""
    running = is_service_running()
    pid = get_service_pid()
    
    return {
        "running": running,
        "pid": pid if running else None,
        "url": "http://127.0.0.1:8888" if running else None,
        "service_dir": str(SERVICE_DIR)
    }


def open_webpage():
    """在浏览器中打开服务页面"""
    import webbrowser
    webbrowser.open(BASE_URL)
    return {"success": True, "message": f"已打开 {BASE_URL}"}


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法：python file_manager.py <command> [args]")
        print("命令:")
        print("  start                 - 启动服务")
        print("  stop                  - 停止服务")
        print("  restart               - 重启服务")
        print("  status                - 服务状态")
        print("  open                  - 打开 Web 页面")
        print("  list [path]           - 列出文件")
        print("  cat <path>            - 查看文件内容")
        print("  search <query>        - 搜索文件")
        print("  stats                 - 统计信息")
        print("  delete <path>         - 删除文件/目录")
        print("  mkdir <path> <name>   - 创建目录")
        print("  note <path> [note]    - 获取/设置备注")
        print("  move <source> <dest>  - 移动文件/目录")
        print("  download <path> [save_path] - 下载文件/目录")
        print("  tree [path]           - 显示目录树")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    # 服务管理命令
    if cmd == "start":
        result = start_service()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result.get("success") else 1)
    
    elif cmd == "stop":
        result = stop_service()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result.get("success") else 1)
    
    elif cmd == "restart":
        stop_service()
        time.sleep(1)
        result = start_service()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result.get("success") else 1)
    
    elif cmd == "status":
        result = service_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    
    elif cmd == "open":
        result = open_webpage()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    
    # 文件管理命令
    if cmd == "list":
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        result = list_files(path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "cat":
        if len(sys.argv) < 3:
            print("错误：缺少文件路径")
            sys.exit(1)
        result = get_file_content(sys.argv[2])
        if "content" in result:
            print(result["content"])
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("错误：缺少搜索关键词")
            sys.exit(1)
        result = search_files(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "stats":
        result = get_stats()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("错误：缺少路径")
            sys.exit(1)
        result = delete_item(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "mkdir":
        if len(sys.argv) < 4:
            print("错误：用法 mkdir <path> <name>")
            sys.exit(1)
        result = create_directory(sys.argv[2], sys.argv[3])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "note":
        if len(sys.argv) < 3:
            print("错误：缺少路径")
            sys.exit(1)
        path = sys.argv[2]
        if len(sys.argv) > 3:
            note = " ".join(sys.argv[3:])
            result = save_note(path, note)
        else:
            result = get_note(path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "move":
        if len(sys.argv) < 4:
            print("错误：用法 move <source> <dest>")
            sys.exit(1)
        result = move_item(sys.argv[2], sys.argv[3])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "download":
        if len(sys.argv) < 3:
            print("错误：缺少路径")
            sys.exit(1)
        save_path = sys.argv[3] if len(sys.argv) > 3 else None
        result = download_item(sys.argv[2], save_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "tree":
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        result = get_tree(path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
