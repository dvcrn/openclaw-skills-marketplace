#!/usr/bin/env python3
"""
最终版SQLite密码管理系统
方案A：使用SQLite数据库 + 简单加密
"""

import sqlite3
import json
import os
import base64
from datetime import datetime
from typing import Dict, Optional, List
import hashlib

class FinalSQLiteSecretManager:
    """最终版SQLite密码管理器"""
    
    def __init__(self, db_path="/root/.openclaw/secrets/final_secrets.db"):
        self.db_path = db_path
        self.db_dir = os.path.dirname(db_path)
        self.config_file = os.path.join(self.db_dir, "config.json")
        self.log_dir = os.path.join(self.db_dir, "logs")
        
        # 确保目录存在
        os.makedirs(self.db_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        
        # 初始化助手和权限
        self._init_assistants()
    
    def _simple_encrypt(self, data: str) -> str:
        """简单加密（实际使用应更安全）"""
        # 使用base64编码 + 简单混淆
        encoded = base64.b64encode(data.encode()).decode()
        # 添加简单混淆
        return encoded[::-1]  # 反转字符串
    
    def _simple_decrypt(self, encrypted: str) -> str:
        """简单解密"""
        # 反转回来
        encoded = encrypted[::-1]
        # base64解码
        return base64.b64decode(encoded).decode()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建passwords表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_type TEXT NOT NULL,
            service_name TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password TEXT NOT NULL,
            description TEXT,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(service_type, service_name, username)
        )
        ''')
        
        # 创建access_logs表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assistant_name TEXT NOT NULL,
            action TEXT NOT NULL,
            service_type TEXT,
            service_name TEXT,
            username TEXT,
            success BOOLEAN DEFAULT 1,
            error_message TEXT,
            accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_passwords_service ON passwords(service_type, service_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_assistant ON access_logs(assistant_name, accessed_at)')
        
        conn.commit()
        conn.close()
        
        print("🗄️ 数据库初始化完成")
    
    def _init_assistants(self):
        """初始化助手配置"""
        # 助手权限配置
        self.assistant_permissions = {
            "小新": ["email", "api_keys", "database", "marketing", "sales", "service", "all"],
            "小雅": ["api_keys", "marketing"],
            "小锐": ["api_keys", "sales"],
            "小暖": ["api_keys", "service"]
        }
        
        print("👥 助手权限配置完成")
    
    def _check_permission(self, assistant: str, service_type: str) -> bool:
        """检查权限"""
        permissions = self.assistant_permissions.get(assistant, [])
        
        # 小新有所有权限
        if assistant == "小新":
            return True
        
        return service_type in permissions or "all" in permissions
    
    def _log_access(self, assistant: str, action: str, service_type: str = None,
                   service_name: str = None, username: str = None, success: bool = True,
                   error: str = None):
        """记录访问日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO access_logs 
            (assistant_name, action, service_type, service_name, username, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (assistant, action, service_type, service_name, username, success, error))
            
            conn.commit()
            conn.close()
            
            # 同时写入文件日志
            log_file = os.path.join(self.log_dir, f"access_{datetime.now().strftime('%Y%m%d')}.log")
            log_entry = f"{datetime.now().isoformat()} | {assistant} | {action} | {service_type or ''} | {service_name or ''} | {username or ''} | {'SUCCESS' if success else 'FAILED'} | {error or ''}\n"
            
            with open(log_file, 'a') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"⚠️ 日志记录失败: {e}")
    
    def store_secret(self, assistant: str, service_type: str, service_name: str,
                    username: str, password: str, description: str = "") -> bool:
        """存储秘密"""
        try:
            # 检查权限
            if not self._check_permission(assistant, service_type):
                print(f"❌ {assistant} 没有权限存储 {service_type} 类型的秘密")
                self._log_access(assistant, "STORE", service_type, service_name, username, False, "权限不足")
                return False
            
            # 加密密码
            encrypted = self._simple_encrypt(password)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 插入或更新
            cursor.execute('''
            INSERT OR REPLACE INTO passwords 
            (service_type, service_name, username, encrypted_password, description, created_by, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (service_type, service_name, username, encrypted, description, assistant))
            
            conn.commit()
            conn.close()
            
            self._log_access(assistant, "STORE", service_type, service_name, username, True)
            print(f"✅ {assistant} 成功存储 {service_type}/{service_name}/{username}")
            return True
            
        except Exception as e:
            print(f"❌ 存储失败: {e}")
            self._log_access(assistant, "STORE", service_type, service_name, username, False, str(e))
            return False
    
    def get_secret(self, assistant: str, service_type: str,
                  service_name: str, username: str) -> Optional[str]:
        """获取秘密"""
        try:
            # 检查权限
            if not self._check_permission(assistant, service_type):
                print(f"❌ {assistant} 没有权限访问 {service_type} 类型的秘密")
                self._log_access(assistant, "GET", service_type, service_name, username, False, "权限不足")
                return None
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT encrypted_password
            FROM passwords
            WHERE service_type = ? AND service_name = ? AND username = ?
            ''', (service_type, service_name, username))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                encrypted = result[0]
                password = self._simple_decrypt(encrypted)
                self._log_access(assistant, "GET", service_type, service_name, username, True)
                print(f"✅ {assistant} 成功获取 {service_type}/{service_name}/{username}")
                return password
            else:
                print(f"❌ 未找到秘密: {service_type}/{service_name}/{username}")
                self._log_access(assistant, "GET", service_type, service_name, username, False, "未找到")
                return None
                
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            self._log_access(assistant, "GET", service_type, service_name, username, False, str(e))
            return None
    
    def list_secrets(self, assistant: str, service_type: str = None) -> List[Dict]:
        """列出秘密"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if service_type:
                # 检查权限
                if not self._check_permission(assistant, service_type):
                    print(f"❌ {assistant} 没有权限查看 {service_type} 类型的秘密")
                    return []
                
                cursor.execute('''
                SELECT service_type, service_name, username, description, created_by, created_at
                FROM passwords
                WHERE service_type = ?
                ORDER BY service_type, service_name, username
                ''', (service_type,))
            else:
                # 获取助手有权限的所有秘密
                allowed_types = [t for t in ["email", "api_keys", "database", "marketing", "sales", "service"] 
                               if self._check_permission(assistant, t)]
                
                if not allowed_types:
                    return []
                
                # 构建查询
                placeholders = ','.join(['?'] * len(allowed_types))
                cursor.execute(f'''
                SELECT service_type, service_name, username, description, created_by, created_at
                FROM passwords
                WHERE service_type IN ({placeholders})
                ORDER BY service_type, service_name, username
                ''', allowed_types)
            
            results = cursor.fetchall()
            conn.close()
            
            secrets = []
            for row in results:
                secrets.append({
                    "service_type": row[0],
                    "service_name": row[1],
                    "username": row[2],
                    "description": row[3],
                    "created_by": row[4],
                    "created_at": row[5]
                })
            
            self._log_access(assistant, "LIST", service_type, None, None, True)
            return secrets
            
        except Exception as e:
            print(f"❌ 列出失败: {e}")
            self._log_access(assistant, "LIST", service_type, None, None, False, str(e))
            return []
    
    def delete_secret(self, assistant: str, service_type: str,
                     service_name: str, username: str) -> bool:
        """删除秘密"""
        try:
            # 只有小新可以删除
            if assistant != "小新":
                print("❌ 只有小新可以删除秘密")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            DELETE FROM passwords
            WHERE service_type = ? AND service_name = ? AND username = ?
            ''', (service_type, service_name, username))
            
            affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if affected > 0:
                self._log_access(assistant, "DELETE", service_type, service_name, username, True)
                print(f"✅ 成功删除 {service_type}/{service_name}/{username}")
                return True
            else:
                print(f"❌ 未找到秘密: {service_type}/{service_name}/{username}")
                self._log_access(assistant, "DELETE", service_type, service_name, username, False, "未找到")
                return False
                
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            self._log_access(assistant, "DELETE", service_type, service_name, username, False, str(e))
            return False
    
    def get_stats(self) -> Dict:
        """获取统计"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM passwords')
            total = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT service_type) FROM passwords')
            types = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT created_by) FROM passwords')
            assistants = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM access_logs WHERE success = 1')
            success = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM access_logs WHERE success = 0')
            failed = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_passwords": total,
                "service_types": types,
                "assistants_with_secrets": assistants,
                "successful_accesses": success,
                "failed_accesses": failed,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 获取统计失败: {e}")
            return {}
    
    def backup(self) -> bool:
        """备份数据库"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.db_dir, f"backup_{timestamp}.db")
            
            import shutil
            shutil.copy2(self.db_path, backup_file)
            
            print(f"✅ 备份完成: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return False
    
    def export_config(self, output_file: str) -> bool:
        """导出配置"""
        try:
            stats = self.get_stats()
            
            config = {
                "export_time": datetime.now().isoformat(),
                "database_path": self.db_path,
                "statistics": stats,
                "assistant_permissions": self.assistant_permissions
            }
            
            with open(output_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 配置导出成功: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False

# 命令行接口
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="SQLite密码管理系统")
    parser.add_argument("assistant", help="助手名称")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # store命令
    store_parser = subparsers.add_parser("store", help="存储密码")
    store_parser.add_argument("service_type", help="服务类型")
    store_parser.add_argument("service_name", help="服务名称")
    store_parser.add_argument("username", help="用户名")
    store_parser.add_argument("--description", help="描述", default="")
    
    # get命令
    get_parser = subparsers.add_parser("get", help="获取密码")
    get_parser.add_argument("service_type", help="服务类型")
    get_parser.add_argument("service_name", help="服务名称")
    get_parser.add_argument("username", help="用户名")
    
    # list命令
    list_parser = subparsers.add_parser("list", help="列出秘密")
    list_parser.add_argument("--service-type", help="服务类型")
    
    # delete命令
    delete_parser = subparsers.add_parser("delete", help="删除密码")
    delete_parser.add_argument("service_type", help="服务类型")
    delete_parser.add_argument("service_name", help="服务名称")
    delete_parser.add_argument("username", help="用户名")
    
    # stats命令
    subparsers.add_parser("stats", help="查看统计")
    
    # backup命令
    subparsers.add_parser("backup", help="备份数据库")
    
    # export命令
    export_parser = subparsers.add_parser("export", help="导出配置")
    export_parser.add_argument("output", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 验证助手
    valid_assistants = ["小新", "小雅", "小锐", "小暖"]
    if args.assistant not in valid_assistants:
        print(f"❌ 无效助手。可用: {', '.join(valid_assistants)}")
        return
    
    manager = FinalSQLiteSecretManager()
    
    if args.command == "store":
        print(f"请输入 {args.service_name}/{args.username} 的密码:")
        password = input()
        manager.store_secret(
            args.assistant,
            args.service_type,
            args.service_name,
            args.username,
            password,
            args.description
        )
    
    elif args.command == "get":
        password = manager.get_secret(
            args.assistant,
            args.service_type,
            args.service_name,
            args.username
        )
        if password:
            print(f"🔐 密码: {password}")
        else:
            print("❌ 未找到或没有权限")
    
    elif args.command == "list":
        secrets = manager.list_secrets(args.assistant, args.service_type)
        count = len(secrets)
        if args.service_type:
            print(f"📋 {args.assistant} 的 {args.service_type} 秘密 ({count} 个):")
        else:
            print(f"📋 {args.assistant} 的所有秘密 ({count} 个):")
        
        for secret in secrets:
            print(f"  • {secret['service_type']}/{secret['service_name']}/{secret['username']}")
            if secret['description']:
                print(f"    描述: {secret['description']}")
    
    elif args.command == "delete":
        manager.delete_secret(
            args.assistant,
            args.service_type,
            args.service_name,
            args.username
        )
    
    elif args.command == "stats":
        stats = manager.get_stats()
        print("📊 系统统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif args.command == "backup":
        manager.backup()
    
    elif args.command == "export":
        manager.export_config(args.output)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()