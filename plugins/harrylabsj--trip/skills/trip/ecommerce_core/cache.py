"""
Data caching for e-commerce platforms
"""

import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


class DataCache:
    """Cache for e-commerce data (search results, prices, etc.)"""
    
    def __init__(self, db_name: str = 'ecommerce.db'):
        """
        Initialize cache
        
        Args:
            db_name: Database file name
        """
        self._data_dir = Path.home() / '.openclaw' / 'data' / 'ecommerce'
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self._data_dir / db_name
        self._init_db()
        
    def _init_db(self):
        """Initialize cache database"""
        conn = sqlite3.connect(str(self._db_path))
        cursor = conn.cursor()
        
        # Cache table for general data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                data_type TEXT,
                platform TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        # Search results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                keyword TEXT,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                product_id TEXT,
                product_url TEXT,
                price REAL,
                currency TEXT DEFAULT 'CNY',
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_platform ON cache(platform)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_platform_keyword ON search_results(platform, keyword)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_platform_product ON price_history(platform, product_id)')
        
        conn.commit()
        conn.close()
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value, expires_at FROM cache WHERE key = ?
            ''', (key,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
                
            value, expires_at = row
            
            # Check expiration
            if expires_at and datetime.now().timestamp() > expires_at:
                self.delete(key)
                return None
                
            return json.loads(value)
            
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
            
    def set(self, key: str, value: Any, 
            ttl_minutes: int = 60, 
            data_type: str = 'general',
            platform: Optional[str] = None) -> bool:
        """
        Set cached value
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_minutes: Time to live in minutes
            data_type: Type of data
            platform: Platform identifier
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            expires_at = datetime.now().timestamp() + (ttl_minutes * 60)
            
            cursor.execute('''
                INSERT OR REPLACE INTO cache 
                (key, value, data_type, platform, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                key,
                json.dumps(value),
                data_type,
                platform,
                expires_at
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
            
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM cache WHERE key = ?', (key,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
            
    def clear_expired(self) -> int:
        """Clear expired cache entries"""
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM cache WHERE expires_at < ?
            ''', (datetime.now().timestamp(),))
            
            count = cursor.rowcount
            conn.commit()
            conn.close()
            return count
            
        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0
            
    def save_search_results(self, platform: str, keyword: str, 
                           results: List[Dict]) -> bool:
        """
        Save search results
        
        Args:
            platform: Platform identifier
            keyword: Search keyword
            results: Search results list
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO search_results (platform, keyword, results)
                VALUES (?, ?, ?)
            ''', (platform, keyword, json.dumps(results)))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Save search error: {e}")
            return False
            
    def get_search_results(self, platform: str, keyword: str,
                          max_age_hours: int = 24) -> Optional[List[Dict]]:
        """
        Get cached search results
        
        Args:
            platform: Platform identifier
            keyword: Search keyword
            max_age_hours: Maximum age of results
            
        Returns:
            Cached results or None
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            cutoff = datetime.now() - timedelta(hours=max_age_hours)
            
            cursor.execute('''
                SELECT results FROM search_results
                WHERE platform = ? AND keyword = ? AND created_at > ?
                ORDER BY created_at DESC LIMIT 1
            ''', (platform, keyword, cutoff.isoformat()))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return json.loads(row[0])
            return None
            
        except Exception as e:
            print(f"Get search error: {e}")
            return None
            
    def record_price(self, platform: str, product_id: str,
                    product_url: str, price: float,
                    currency: str = 'CNY') -> bool:
        """
        Record product price
        
        Args:
            platform: Platform identifier
            product_id: Product identifier
            product_url: Product URL
            price: Current price
            currency: Currency code
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO price_history 
                (platform, product_id, product_url, price, currency)
                VALUES (?, ?, ?, ?, ?)
            ''', (platform, product_id, product_url, price, currency))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Record price error: {e}")
            return False
            
    def get_price_history(self, platform: str, product_id: str,
                         days: int = 30) -> List[Dict]:
        """
        Get price history for a product
        
        Args:
            platform: Platform identifier
            product_id: Product identifier
            days: Number of days to retrieve
            
        Returns:
            List of price records
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            cursor = conn.cursor()
            
            cutoff = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT price, currency, recorded_at
                FROM price_history
                WHERE platform = ? AND product_id = ? AND recorded_at > ?
                ORDER BY recorded_at ASC
            ''', (platform, product_id, cutoff.isoformat()))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'price': row[0],
                    'currency': row[1],
                    'recorded_at': row[2]
                })
                
            conn.close()
            return results
            
        except Exception as e:
            print(f"Get price history error: {e}")
            return []
            
    @staticmethod
    def make_key(*args) -> str:
        """Create cache key from arguments"""
        key_str = '|'.join(str(a) for a in args)
        return hashlib.md5(key_str.encode()).hexdigest()
