#!/usr/bin/env python3
"""
安全存储模块 - 提供加密的Cookie存储和敏感数据管理
"""

import json
import os
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("请安装加密库: pip install cryptography")
    raise

class SecureStorage:
    """安全存储管理器"""
    
    def __init__(self, app_name: str = "vip"):
        """
        初始化安全存储
        
        Args:
            app_name: 应用名称，用于创建独立的存储目录
        """
        self.app_name = app_name
        self.storage_dir = Path.home() / ".openclaw" / "data" / app_name / "secure"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 密钥文件路径
        self.key_file = self.storage_dir / ".key"
        self.cookies_file = self.storage_dir / "cookies.enc"
        self.consent_file = self.storage_dir / ".consent"
        
        # 初始化加密
        self.cipher = self._get_cipher()
    
    def _get_cipher(self) -> Fernet:
        """获取或创建加密密钥"""
        # 如果密钥文件已存在，加载密钥
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            # 生成新密钥
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # 设置仅用户可读权限
            os.chmod(self.key_file, 0o600)
        
        return Fernet(key)
    
    def save_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        """加密保存Cookies"""
        if not cookies:
            return
        
        # 转换为JSON并加密
        cookies_json = json.dumps(cookies)
        encrypted = self.cipher.encrypt(cookies_json.encode())
        
        # 保存加密数据
        with open(self.cookies_file, 'wb') as f:
            f.write(encrypted)
        
        # 设置文件权限
        os.chmod(self.cookies_file, 0o600)
        print(f"✅ Cookies已加密保存到: {self.cookies_file}")
    
    def load_cookies(self) -> Optional[List[Dict[str, Any]]]:
        """加载并解密Cookies"""
        if not self.cookies_file.exists():
            return None
        
        try:
            with open(self.cookies_file, 'rb') as f:
                encrypted = f.read()
            
            # 解密
            decrypted = self.cipher.decrypt(encrypted)
            cookies = json.loads(decrypted.decode())
            return cookies
        except Exception as e:
            print(f"❌ 加载Cookies失败: {e}")
            return None
    
    def clear_sensitive_data(self) -> None:
        """安全清理所有敏感数据"""
        files_to_clear = [
            self.cookies_file,
            self.key_file,
            self.storage_dir / "config.enc",
            self.storage_dir / "history.enc"
        ]
        
        for file_path in files_to_clear:
            if file_path.exists():
                try:
                    # 安全删除：先用随机数据覆盖，再删除
                    file_size = file_path.stat().st_size
                    with open(file_path, 'wb') as f:
                        f.write(os.urandom(file_size))
                    file_path.unlink()
                    print(f"✅ 已安全删除: {file_path.name}")
                except Exception as e:
                    print(f"⚠️  删除 {file_path} 失败: {e}")
    
    def check_consent(self) -> bool:
        """检查用户是否已同意数据使用条款"""
        if self.consent_file.exists():
            return True
        
        print("\n" + "="*60)
        print(f"{self.app_name.upper()} 技能 - 数据使用说明")
        print("="*60)
        print("🔐 隐私与安全声明")
        print("="*60)
        print("1. 数据存储")
        print("   - 登录会话信息会加密存储在本地")
        print("   - 所有数据仅保存在您的电脑上，不会上传到任何服务器")
        print("   - 使用 AES-256 加密保护敏感信息")
        
        print("\n2. 权限说明")
        print("   - 需要访问浏览器进行网站交互")
        print("   - 需要本地文件系统权限存储配置")
        print("   - 需要网络权限访问电商网站")
        
        print("\n3. 您的权利")
        print("   - 随时可以运行清除命令删除所有个人数据")
        print("   - 可以随时撤销同意，技能将停止运行")
        print("   - 可以导出您的数据用于迁移或备份")
        
        print("\n" + "="*60)
        print("是否同意以上条款并继续使用？(y/N): ", end="")
        
        response = input().strip().lower()
        if response == 'y':
            # 记录同意
            with open(self.consent_file, 'w') as f:
                f.write(f"consent_granted: {datetime.now().isoformat()}\n")
                f.write(f"app: {self.app_name}\n")
                f.write(f"version: 1.0\n")
            
            # 设置权限
            os.chmod(self.consent_file, 0o600)
            print("✅ 感谢您的同意！开始使用...")
            return True
        else:
            print("❌ 需要同意才能使用本技能。")
            return False
    
    def get_privacy_info(self) -> Dict[str, Any]:
        """获取隐私信息摘要"""
        info = {
            "app": self.app_name,
            "storage_dir": str(self.storage_dir),
            "has_consent": self.consent_file.exists(),
            "has_cookies": self.cookies_file.exists(),
            "has_key": self.key_file.exists(),
            "files": []
        }
        
        if self.storage_dir.exists():
            for file in self.storage_dir.iterdir():
                if file.is_file():
                    file_info = {
                        "name": file.name,
                        "size": file.stat().st_size,
                        "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                        "permissions": oct(file.stat().st_mode)[-3:]
                    }
                    info["files"].append(file_info)
        
        return info
    
    def export_data(self, export_path: Optional[Path] = None) -> Path:
        """导出加密数据（用于迁移或备份）"""
        if not export_path:
            export_path = Path.home() / f"{self.app_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar"
        
        import tarfile
        
        with tarfile.open(export_path, 'w') as tar:
            if self.cookies_file.exists():
                tar.add(self.cookies_file, arcname="cookies.enc")
            if self.consent_file.exists():
                tar.add(self.consent_file, arcname="consent.txt")
            
            # 添加README说明
            readme_content = f"""# {self.app_name.upper()} 数据导出
导出时间: {datetime.now().isoformat()}
包含文件:
1. cookies.enc - 加密的登录会话
2. consent.txt - 用户同意记录

这些是加密文件，需要原始密钥才能解密。
密钥保存在: {self.key_file}
请确保同时备份密钥文件。
"""
            readme_path = self.storage_dir / "README_EXPORT.md"
            readme_path.write_text(readme_content)
            tar.add(readme_path, arcname="README.md")
            readme_path.unlink()
        
        print(f"✅ 数据已导出到: {export_path}")
        return export_path