"""
RPC Manager Module

Provides RPC fallback and session stickiness for blockchain operations.
Inspired by xaut-trade's RPC resilience design.

Key Features:
- Automatic fallback to secondary RPC nodes on network errors
- Session stickiness: once a fallback is selected, use it for the entire session
- Clear distinction between network errors (should fallback) and business errors (should not)
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class RPCErrors(Exception):
    """Exception raised when all RPC endpoints fail."""
    pass


@dataclass
class RPCConfig:
    """RPC configuration for a single chain."""
    chain: str
    endpoints: List[str]
    timeout_seconds: int = 10
    fallback_enabled: bool = True
    session_sticky: bool = True


@dataclass
class RPCStatus:
    """Status of an RPC endpoint."""
    url: str
    is_active: bool = False
    last_error: Optional[str] = None
    last_success_time: Optional[float] = None
    block_number: Optional[int] = None


class RPCManager:
    """
    Manages RPC connections with fallback support.
    
    Design Philosophy (from xaut-trade):
    - Only trigger fallback for NETWORK errors (429, 502, 503, timeout, connection refused)
    - Do NOT trigger fallback for business errors (insufficient balance, contract revert, etc.)
    - Once a fallback is selected, use it for the entire session (session stickiness)
    
    Usage:
        manager = RPCManager(config)
        
        # Get active RPC URL (may be primary or fallback)
        rpc_url = manager.get_active_rpc("base")
        
        # Make request with automatic fallback
        result = manager.request("base", {
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [...],
            "id": 1
        })
    """
    
    # Error patterns that should trigger fallback
    NETWORK_ERROR_PATTERNS = [
        "429",           # Too Many Requests
        "502",           # Bad Gateway
        "503",           # Service Unavailable
        "timeout",
        "timed out",
        "connection refused",
        "ECONNREFUSED",
        "ENOTFOUND",
        "EAI_AGAIN",     # DNS lookup error
        "rate limit",
        "too many requests",
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize RPC Manager.
        
        Args:
            config: Full config dict from config.json
        """
        self.config = config
        self.rpc_config = config.get("rpc", {})
        
        # Session state: active RPC per chain
        self._active_rpc: Dict[str, str] = {}
        
        # Status tracking
        self._rpc_status: Dict[str, Dict[str, RPCStatus]] = {}
        
        # Initialize status for all configured endpoints
        self._init_status()
    
    def _init_status(self):
        """Initialize RPC status tracking."""
        endpoints_config = self.rpc_config.get("endpoints", {})
        
        for chain, urls in endpoints_config.items():
            self._rpc_status[chain] = {}
            for url in urls:
                self._rpc_status[chain][url] = RPCStatus(url=url)
    
    def get_endpoints(self, chain: str) -> List[str]:
        """Get all configured endpoints for a chain."""
        # Support new config structure: chain.rpc
        chain_config = self.config.get("chain", {})
        rpc_endpoints = chain_config.get("rpc", {})
        if rpc_endpoints:
            return rpc_endpoints.get(chain, [])
        
        # Fallback to old structure: rpc.endpoints
        return self.rpc_config.get("endpoints", {}).get(chain, [])
    
    def get_active_rpc(self, chain: str) -> Optional[str]:
        """
        Get the currently active RPC URL for a chain.
        
        Returns the session-sticky fallback if one was selected,
        otherwise returns the primary endpoint.
        """
        # Check session sticky fallback
        if self.rpc_config.get("session_sticky", True):
            if chain in self._active_rpc:
                return self._active_rpc[chain]
        
        # Return primary (first) endpoint
        endpoints = self.get_endpoints(chain)
        return endpoints[0] if endpoints else None
    
    def set_active_rpc(self, chain: str, url: str):
        """Set the active RPC for a chain (for session stickiness)."""
        if self.rpc_config.get("session_sticky", True):
            self._active_rpc[chain] = url
        
        # Update status
        if chain in self._rpc_status and url in self._rpc_status[chain]:
            self._rpc_status[chain][url].is_active = True
            self._rpc_status[chain][url].last_success_time = time.time()
    
    def is_network_error(self, error: Exception) -> bool:
        """
        Check if an error is a network error that should trigger fallback.
        
        Network errors: 429, 502, 503, timeout, connection refused
        Business errors: insufficient balance, contract revert, invalid params
        """
        error_str = str(error).lower()
        
        for pattern in self.NETWORK_ERROR_PATTERNS:
            if pattern.lower() in error_str:
                return True
        
        return False
    
    def health_check(self, chain: str, url: str) -> tuple[bool, Optional[int]]:
        """
        Perform a quick health check on an RPC endpoint.
        
        Returns:
            (success, block_number) tuple
        """
        timeout = self.rpc_config.get("timeout_seconds", 10)
        
        try:
            response = requests.post(
                url,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_blockNumber",
                    "params": [],
                    "id": 1
                },
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    block_number = int(data["result"], 16)
                    return True, block_number
            
            return False, None
        
        except Exception:
            return False, None
    
    def find_healthy_fallback(self, chain: str) -> Optional[str]:
        """
        Find a healthy fallback RPC endpoint.
        
        Tries each endpoint in order, returns the first one that responds.
        """
        endpoints = self.get_endpoints(chain)
        current_active = self.get_active_rpc(chain)
        
        for url in endpoints:
            # Skip the current active (which failed)
            if url == current_active:
                continue
            
            success, block = self.health_check(chain, url)
            
            if success:
                self.set_active_rpc(chain, url)
                return url
        
        return None
    
    def request(
        self,
        chain: str,
        payload: Dict[str, Any],
        prefer_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make an RPC request with automatic fallback.
        
        Args:
            chain: Chain name (base, ethereum)
            payload: JSON-RPC payload
            prefer_url: Preferred URL (optional, overrides session state)
        
        Returns:
            JSON-RPC response
        
        Raises:
            RPCErrors: If all endpoints fail
        """
        timeout = self.rpc_config.get("timeout_seconds", 10)
        fallback_enabled = self.rpc_config.get("fallback_enabled", True)
        
        # Determine which URL to use
        if prefer_url:
            url = prefer_url
        else:
            url = self.get_active_rpc(chain)
        
        if not url:
            raise RPCErrors(f"No RPC endpoint configured for chain: {chain}")
        
        # Try the primary/active URL
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for JSON-RPC error (business error, don't fallback)
                if "error" in result:
                    return result
                
                # Success
                self.set_active_rpc(chain, url)
                return result
            
            # Non-200 status - check if it's a network error
            if self._is_status_network_error(response.status_code):
                raise requests.exceptions.RequestException(f"HTTP {response.status_code}")
            
            # Other HTTP errors - return as-is
            return {"error": {"code": response.status_code, "message": response.text}}
        
        except requests.exceptions.RequestException as e:
            # Check if we should try fallback
            if not fallback_enabled:
                raise RPCErrors(f"RPC request failed: {str(e)}")
            
            if not self.is_network_error(e):
                # Business error, don't fallback
                raise RPCErrors(f"RPC request failed: {str(e)}")
            
            # Try fallback
            fallback_url = self.find_healthy_fallback(chain)
            
            if fallback_url:
                # Retry with fallback
                try:
                    response = requests.post(
                        fallback_url,
                        json=payload,
                        timeout=timeout,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        self.set_active_rpc(chain, fallback_url)
                        return result
                
                except requests.exceptions.RequestException:
                    pass
            
            # All endpoints failed
            raise RPCErrors(
                f"All RPC endpoints failed for {chain}. "
                f"Tried: {len(self.get_endpoints(chain))} endpoints."
            )
    
    def _is_status_network_error(self, status_code: int) -> bool:
        """Check if HTTP status code indicates a network error."""
        network_status_codes = [429, 502, 503, 504]
        return status_code in network_status_codes
    
    def get_status_report(self, chain: str) -> Dict[str, Any]:
        """Get status report for all RPC endpoints of a chain."""
        endpoints = self.get_endpoints(chain)
        active = self.get_active_rpc(chain)
        
        report = {
            "chain": chain,
            "active_rpc": active,
            "fallback_enabled": self.rpc_config.get("fallback_enabled", True),
            "session_sticky": self.rpc_config.get("session_sticky", True),
            "endpoints": []
        }
        
        for url in endpoints:
            status = self._rpc_status.get(chain, {}).get(url)
            report["endpoints"].append({
                "url": url,
                "is_active": url == active,
                "last_error": status.last_error if status else None,
                "last_success_time": status.last_success_time if status else None
            })
        
        return report


# Singleton instance for session-level stickiness
_rpc_manager_instance: Optional[RPCManager] = None


def get_rpc_manager(config: Optional[Dict[str, Any]] = None) -> RPCManager:
    """
    Get or create the singleton RPC manager.
    
    Args:
        config: Config dict (required on first call)
    
    Returns:
        RPCManager instance
    """
    global _rpc_manager_instance
    
    if _rpc_manager_instance is None:
        if config is None:
            raise ValueError("Config required for first initialization")
        _rpc_manager_instance = RPCManager(config)
    
    return _rpc_manager_instance


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from config.json."""
    if config_path is None:
        # Try multiple paths to find config.json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path 1: scripts/utils/.. -> skills/web3-investor/
        skill_dir = os.path.dirname(os.path.dirname(script_dir))
        config_path = os.path.join(skill_dir, "config", "config.json")
        
        # Path 2: If running from workspace root
        if not os.path.exists(config_path):
            config_path = "skills/web3-investor/config/config.json"
        
        # Path 3: If running from skill directory
        if not os.path.exists(config_path):
            config_path = "config/config.json"
    
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    
    return {}


if __name__ == "__main__":
    # Simple test
    config = load_config()
    manager = RPCManager(config)
    
    print("RPC Manager Test")
    print("=" * 50)
    
    for chain in ["base", "ethereum"]:
        print(f"\n{chain.upper()}:")
        print(f"  Primary: {manager.get_endpoints(chain)[0] if manager.get_endpoints(chain) else 'N/A'}")
        print(f"  Active: {manager.get_active_rpc(chain)}")
        
        # Health check
        url = manager.get_active_rpc(chain)
        if url:
            success, block = manager.health_check(chain, url)
            print(f"  Health: {'✅ OK' if success else '❌ Failed'}")
            if block:
                print(f"  Block: #{block}")
    
    print("\n" + "=" * 50)
    print("Status Report:")
    print(json.dumps(manager.get_status_report("base"), indent=2))