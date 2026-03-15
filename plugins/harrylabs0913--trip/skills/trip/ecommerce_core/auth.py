"""
Authentication manager for e-commerce platforms
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class AuthManager:
    """Manages authentication sessions for e-commerce platforms"""
    
    def __init__(self):
        self._data_dir = Path.home() / '.openclaw' / 'data' / 'ecommerce'
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self._data_dir / 'auth.db'
        self._init_db()
        
    def _init_db(self):
        """Initialize authentication database"""
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                platform TEXT PRIMARY KEY,
                session_data TEXT,
                cookies TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def save_session(self, platform: str, session_data: Dict[str, Any], 
                     cookies: Optional[list] = None, 
                     expires_in_days: int = 7) -> bool:
        """
        Save authentication session
        
        Args:
            platform: Platform identifier (e.g., 'jd', 'taobao')
            session_data: Session information (tokens, user info, etc.)
            cookies: Browser cookies
            expires_in_days: Session expiration time
            
        Returns:
            True if saved successfully
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            expires_at = datetime.now().timestamp() + (expires_in_days * 86400)
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (platform, session_data, cookies, updated_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                platform,
                json.dumps(session_data),
                json.dumps(cookies) if cookies else None,
                datetime.now().isoformat(),
                expires_at
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Failed to save session: {e}")
            return False
            
    def load_session(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        Load authentication session
        
        Args:
            platform: Platform identifier
            
        Returns:
            Session data or None if not found/expired
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_data, cookies, expires_at 
                FROM sessions 
                WHERE platform = ?
            ''', (platform,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
                
            session_data, cookies, expires_at = row
            
            # Check expiration
            if expires_at and datetime.now().timestamp() > expires_at:
                self.clear_session(platform)
                return None
                
            result = json.loads(session_data)
            if cookies:
                result['cookies'] = json.loads(cookies)
                
            return result
            
        except Exception as e:
            print(f"Failed to load session: {e}")
            return None
            
    def clear_session(self, platform: str) -> bool:
        """
        Clear authentication session
        
        Args:
            platform: Platform identifier
            
        Returns:
            True if cleared successfully
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM sessions WHERE platform = ?', (platform,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Failed to clear session: {e}")
            return False
            
    def is_logged_in(self, platform: str) -> bool:
        """
        Check if platform has valid session
        
        Args:
            platform: Platform identifier
            
        Returns:
            True if valid session exists
        """
        return self.load_session(platform) is not None
        
    def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all active sessions
        
        Returns:
            Dictionary of platform -> session info
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT platform, session_data, expires_at 
                FROM sessions
            ''')
            
            sessions = {}
            current_time = datetime.now().timestamp()
            
            for row in cursor.fetchall():
                platform, session_data, expires_at = row
                
                # Skip expired sessions
                if expires_at and current_time > expires_at:
                    continue
                    
                sessions[platform] = {
                    'data': json.loads(session_data),
                    'expires_at': expires_at
                }
                
            conn.close()
            return sessions
            
        except Exception as e:
            print(f"Failed to list sessions: {e}")
            return {}
