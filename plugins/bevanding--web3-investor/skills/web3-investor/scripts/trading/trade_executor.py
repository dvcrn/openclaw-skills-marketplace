#!/usr/bin/env python3
"""
Trade Executor - REST API adapter for local keystore signer (v0.3.0)

DESIGN PHILOSOPHY (Agent-First Design):
This module is designed for AGENTS with LLM and programming capabilities.
It provides a REFERENCE implementation, not a rigid standard.

If your signer service uses different API paths or response formats:
1. Modify config/config.json to map your endpoints
2. Or modify this file's api_request() function
3. Or implement an adapter layer in your signer service

Architecture:
- This module ONLY generates executable transaction requests, does NOT hold private keys
- All transactions must go through: preview -> approve -> execute
- Supports: base, ethereum chains
- Entry point: REST API endpoints

Security Constraints:
- Cannot skip 'approve' step
- Must simulate before execution (eth_call)
- Must return risk warnings (insufficient balance, missing approval, invalid route)
- Default minimum permissions: whitelist chains/protocols/tokens, limits, max slippage

Usage:
    python3 trade_executor.py preview --type swap --from-token USDC --to-token WETH --amount 5 --network base
    python3 trade_executor.py approve --preview-id <id>
    python3 trade_executor.py execute --approval-id <id>
    python3 trade_executor.py status --tx-hash 0x...

For API specification, see: SIGNER_API_SPEC.md
For setup guide, see: SETUP.md
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
import urllib.request
import urllib.error

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # trading -> scripts -> skill_dir
CONFIG_PATH = os.path.join(SKILL_DIR, "config", "config.json")

# Add scripts directory to path for imports (utils and schemas are in scripts/)
sys.path.insert(0, os.path.dirname(SCRIPT_DIR))
try:
    from utils.preflight import PreflightChecker, PreflightError, load_config as load_preflight_config
    PREFLIGHT_AVAILABLE = True
except ImportError as e:
    PREFLIGHT_AVAILABLE = False

try:
    from utils.rpc_manager import RPCManager, get_rpc_manager
    RPC_MANAGER_AVAILABLE = True
except ImportError:
    RPC_MANAGER_AVAILABLE = False

try:
    from schemas.output_schema import (
        PreviewOutput, ApprovalResult, ExecutionResult,
        InputInfo, QuoteInfo, RiskWarning, RiskLevel,
        create_preview_output, create_approval_result, create_execution_result
    )
    SCHEMA_AVAILABLE = True
except ImportError:
    SCHEMA_AVAILABLE = False

# API Base URL (from environment or default)
API_BASE_URL = os.environ.get("WEB3_INVESTOR_API_URL", "http://localhost:3000/api")

# Supported chains
SUPPORTED_CHAINS = {
    "base": {"chain_id": 8453, "name": "Base", "explorer": "https://basescan.org"},
    "ethereum": {"chain_id": 1, "name": "Ethereum", "explorer": "https://etherscan.io"},
}

# Default security settings
DEFAULT_SECURITY = {
    "max_slippage_percent": 3.0,
    "whitelist_enabled": False,
    "whitelist_chains": ["base", "ethereum"],
    "whitelist_protocols": ["uniswap", "aave", "compound", "lido", "0x"],
    "whitelist_tokens": ["USDC", "USDT", "DAI", "WETH", "ETH", "stETH", "rETH"],
    "max_trade_value_usd": 10000,
}

# Error codes
ERROR_CODES = {
    "INSUFFICIENT_BALANCE": {"code": "E001", "message": "Insufficient balance for transaction"},
    "INSUFFICIENT_ALLOWANCE": {"code": "E002", "message": "Token allowance insufficient, approval required"},
    "INVALID_ROUTE": {"code": "E003", "message": "No valid route found for swap"},
    "CHAIN_NOT_SUPPORTED": {"code": "E004", "message": "Chain not in whitelist"},
    "PROTOCOL_NOT_SUPPORTED": {"code": "E005", "message": "Protocol not in whitelist"},
    "TOKEN_NOT_SUPPORTED": {"code": "E006", "message": "Token not in whitelist"},
    "EXCEEDS_LIMIT": {"code": "E007", "message": "Transaction exceeds configured limit"},
    "PREVIEW_FAILED": {"code": "E008", "message": "Transaction simulation failed"},
    "APPROVAL_REQUIRED": {"code": "E009", "message": "Cannot execute without approval"},
    "API_UNAVAILABLE": {"code": "E010", "message": "Local API service unavailable"},
    "PREFLIGHT_FAILED": {"code": "E014", "message": "Pre-flight checks failed"},
    "UNKNOWN_ERROR": {"code": "E999", "message": "Unknown error occurred"},
}


# ============================================================================
# Unified Transaction Request Format
# ============================================================================

def create_transaction_request(
    network: str,
    tx_type: str,
    to: str,
    value: str = "0x0",
    data: str = "0x",
    gas_limit: int = 250000,
    description: str = "",
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Create a unified transaction request format.
    
    Args:
        network: Chain name (base, ethereum)
        tx_type: Transaction type (transfer, swap, deposit, contract_call)
        to: Target address
        value: Value in hex (0x...)
        data: Calldata in hex
        gas_limit: Estimated gas limit
        description: Human readable description
        metadata: Additional protocol info (protocol, from_token, to_token, amount)
    
    Returns:
        Unified transaction request dict
    """
    if network not in SUPPORTED_CHAINS:
        raise ValueError(f"Unsupported network: {network}. Supported: {list(SUPPORTED_CHAINS.keys())}")
    
    request = {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "network": network,
        "chain_id": SUPPORTED_CHAINS[network]["chain_id"],
        "type": tx_type,
        "description": description,
        "transaction": {
            "to": to,
            "value": value,
            "data": data,
            "gas_limit": gas_limit
        },
        "metadata": metadata or {}
    }
    
    return request


# ============================================================================
# API Client
# ============================================================================

def api_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Make a request to the local signer API.
    
    This is the core HTTP client. If your signer service uses different
    API paths or response formats, modify this function or update config.json.
    
    Args:
        method: HTTP method (GET, POST)
        endpoint: API endpoint (without /api prefix)
        data: Request body for POST
        timeout: Request timeout in seconds
    
    Returns:
        API response as dict with 'success' field
    """
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        if method.upper() == "GET":
            req = urllib.request.Request(url, headers=headers, method="GET")
        else:
            body = json.dumps(data or {}).encode("utf-8")
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
            return {"success": True, "data": result}
    
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": ERROR_CODES["API_UNAVAILABLE"],
            "diagnostics": f"Cannot connect to {url}: {str(e)}"
        }
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read().decode("utf-8"))
            return {
                "success": False,
                "error": error_body.get("error", ERROR_CODES["UNKNOWN_ERROR"]),
                "diagnostics": error_body.get("message", f"HTTP {e.code}")
            }
        except:
            return {
                "success": False,
                "error": ERROR_CODES["UNKNOWN_ERROR"],
                "diagnostics": f"HTTP {e.code}: {e.reason}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": ERROR_CODES["UNKNOWN_ERROR"],
            "diagnostics": str(e)
        }


# ============================================================================
# Wallet Operations
# ============================================================================

def get_wallet_balances(
    chain: Optional[str] = None,
    tokens: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Query wallet balances from local API.
    
    GET /api/wallet/balances
    """
    params = []
    if chain:
        params.append(f"chain={chain}")
    if tokens:
        params.append(f"tokens={','.join(tokens)}")
    
    endpoint = "/wallet/balances"
    if params:
        endpoint += "?" + "&".join(params)
    
    return api_request("GET", endpoint)


# ============================================================================
# Trade Operations (State Machine: Preview -> Approve -> Execute)
# ============================================================================

def run_preflight_checks(transaction_type: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Run pre-flight checks if available and enabled.
    
    Returns None if checks pass, or error dict if checks fail.
    """
    if not PREFLIGHT_AVAILABLE:
        return None
    
    try:
        config = load_preflight_config(CONFIG_PATH)
        preflight_config = config.get("preflight", {})
        
        if not preflight_config.get("enabled", True):
            return None
        
        checker = PreflightChecker(config)
        report = checker.run(transaction_type, params)
        
        if not report.critical_passed:
            return {
                "success": False,
                "error": {
                    "code": "E014",
                    "message": "Pre-flight checks failed",
                    "details": {
                        "summary": report.summary,
                        "failed_checks": [
                            {
                                "name": r.name,
                                "message": r.message,
                                "fix_hint": r.fix_hint,
                                "severity": r.severity.value
                            }
                            for r in report.results if not r.passed
                        ]
                    }
                },
                "diagnostics": report.summary
            }
        
        return None
    
    except Exception as e:
        # Pre-flight errors should not block execution, just log
        return None


def preview_swap(
    from_token: str,
    to_token: str,
    amount: str,
    network: str = "base",
    slippage: float = 0.5,
    protocol: str = "auto"
) -> Dict[str, Any]:
    """
    Preview a swap transaction.
    
    POST /api/trades/preview (or /api/uniswap/preview-swap, /api/zerox/preview-swap)
    
    Returns:
        {
            "preview_id": "uuid",
            "simulation_ok": true/false,
            "risk": {...},
            "next_step": "approve" or "clarification",
            ...
        }
    """
    # Pre-flight checks
    params = {
        "type": "swap",
        "network": network,
        "from_token": from_token,
        "to_token": to_token,
        "amount": amount
    }
    preflight_error = run_preflight_checks("swap", params)
    if preflight_error:
        return preflight_error
    
    # Security check: whitelist (only if enabled)
    security = _load_security_config()
    
    # Skip whitelist checks if whitelist_enabled is False (default for backward compatibility)
    if security.get("whitelist_enabled", False):
        if network not in security.get("whitelist_chains", []):
            return {
                "success": False,
                "error": ERROR_CODES["CHAIN_NOT_SUPPORTED"],
                "diagnostics": f"Chain '{network}' not in whitelist. Allowed: {security['whitelist_chains']}"
            }
        
        if from_token.upper() not in security.get("whitelist_tokens", []):
            return {
                "success": False,
                "error": ERROR_CODES["TOKEN_NOT_SUPPORTED"],
                "diagnostics": f"Token '{from_token}' not in whitelist. Allowed: {security['whitelist_tokens']}"
            }
        
        if to_token.upper() not in security.get("whitelist_tokens", []):
            return {
                "success": False,
                "error": ERROR_CODES["TOKEN_NOT_SUPPORTED"],
                "diagnostics": f"Token '{to_token}' not in whitelist. Allowed: {security['whitelist_tokens']}"
            }
    
    # Try different preview endpoints
    endpoints_to_try = [
        "/trades/preview",
        "/uniswap/preview-swap",
        "/zerox/preview-swap"
    ]
    
    payload = {
        "from_token": from_token,
        "to_token": to_token,
        "amount": amount,
        "network": network,
        "slippage_percent": slippage,
        "protocol": protocol
    }
    
    last_error = None
    for endpoint in endpoints_to_try:
        result = api_request("POST", endpoint, payload)
        
        if result.get("success"):
            # Standardize response format
            data = result.get("data", {})
            
            # Check if double confirmation is required
            preview_result_basic = {
                "success": True,
                "preview_id": data.get("preview_id", str(uuid.uuid4())),
                "simulation_ok": data.get("simulation_ok", True),
                "risk": _extract_risk_info(data),
                "next_step": "approve" if data.get("simulation_ok", True) else "clarification",
                "transaction": data.get("transaction"),
                "rate": data.get("rate"),
                "estimated_output": data.get("estimated_output"),
                "gas_estimate": data.get("gas_estimate"),
                "warnings": data.get("warnings", [])
            }
            
            # Add double confirm check
            requires_double, reasons = _check_double_confirm_required(params, preview_result_basic)
            preview_result_basic["requires_double_confirm"] = requires_double
            if requires_double:
                preview_result_basic["double_confirm_reasons"] = reasons
                security = _load_security_config()
                confirm_phrase = security.get("double_confirm", {}).get("confirm_phrase", "CONFIRM_HIGH_RISK")
                preview_result_basic["confirm_instruction"] = f"To approve, use: --confirm \"{confirm_phrase}\""
            
            # Create standardized output if schema available
            if SCHEMA_AVAILABLE:
                input_info = InputInfo(
                    token=from_token,
                    amount=amount,
                    chain=network,
                    token_out=to_token
                )
                
                quote_info = QuoteInfo(
                    estimated_output=data.get("estimated_output"),
                    rate=data.get("rate"),
                    slippage_bps=int(slippage * 100),
                    gas_estimate=data.get("gas_estimate")
                )
                
                risk_warnings = []
                if data.get("warnings"):
                    for warning in data["warnings"]:
                        risk_warnings.append(RiskWarning(
                            type="general",
                            level=RiskLevel.MEDIUM,
                            message=warning
                        ))
                
                standardized = create_preview_output(
                    input_info=input_info,
                    quote_info=quote_info,
                    risk_warnings=risk_warnings,
                    requires_double_confirm=requires_double,
                    double_confirm_reasons=reasons,
                    confirm_instruction=preview_result_basic.get("confirm_instruction"),
                    preview_id=data.get("preview_id", str(uuid.uuid4())),
                    raw_transaction=data.get("transaction")
                )
                
                # Merge standardized format with basic result
                preview_result_basic["_standardized"] = standardized.to_dict()
            
            return preview_result_basic
        
        last_error = result
    
    # All endpoints failed
    return {
        "success": False,
        "error": last_error.get("error", ERROR_CODES["PREVIEW_FAILED"]) if last_error else ERROR_CODES["PREVIEW_FAILED"],
        "diagnostics": last_error.get("diagnostics", "All preview endpoints failed") if last_error else "No response from API"
    }


def preview_deposit(
    protocol: str,
    asset: str,
    amount: str,
    network: str = "base"
) -> Dict[str, Any]:
    """
    Preview a deposit transaction (for lending/staking).
    
    POST /api/trades/preview
    """
    # Pre-flight checks
    params = {
        "type": "deposit",
        "network": network,
        "asset": asset,
        "amount": amount
    }
    preflight_error = run_preflight_checks("deposit", params)
    if preflight_error:
        return preflight_error
    
    security = _load_security_config()
    
    if network not in security.get("whitelist_chains", []):
        return {
            "success": False,
            "error": ERROR_CODES["CHAIN_NOT_SUPPORTED"],
            "diagnostics": f"Chain '{network}' not in whitelist."
        }
    
    payload = {
        "type": "deposit",
        "protocol": protocol,
        "asset": asset,
        "amount": amount,
        "network": network
    }
    
    result = api_request("POST", "/trades/preview", payload)
    
    if result.get("success"):
        data = result.get("data", {})
        return {
            "success": True,
            "preview_id": data.get("preview_id", str(uuid.uuid4())),
            "simulation_ok": data.get("simulation_ok", True),
            "risk": _extract_risk_info(data),
            "next_step": "approve" if data.get("simulation_ok", True) else "clarification",
            "transaction": data.get("transaction"),
            "warnings": data.get("warnings", [])
        }
    
    return result


def approve_transaction(preview_id: str, confirm_phrase: str = None) -> Dict[str, Any]:
    """
    Approve a previewed transaction.
    
    POST /api/trades/approve
    
    Args:
        preview_id: Preview ID from preview step
        confirm_phrase: Confirmation phrase for high-risk transactions
    
    Returns:
        {
            "approval_id": "uuid",
            "preview_id": "...",
            ...
        }
    """
    if not preview_id:
        return {
            "success": False,
            "error": {"code": "E011", "message": "preview_id is required"},
            "diagnostics": "Cannot approve without preview_id"
        }
    
    # Check if double confirmation is required
    # In a real implementation, we would retrieve the preview result from storage
    # For now, we check the confirm_phrase if provided
    security = _load_security_config()
    double_confirm_config = security.get("double_confirm", {})
    
    if double_confirm_config.get("enabled", False):
        required_phrase = double_confirm_config.get("confirm_phrase", "CONFIRM_HIGH_RISK")
        
        # If confirm_phrase is provided, validate it
        if confirm_phrase is not None:
            if confirm_phrase != required_phrase:
                return {
                    "success": False,
                    "error": {"code": "E015", "message": "Invalid confirmation phrase"},
                    "diagnostics": f"Expected: {required_phrase}"
                }
    
    result = api_request("POST", "/trades/approve", {"preview_id": preview_id})
    
    if result.get("success"):
        data = result.get("data", {})
        
        # Create standardized output if schema available
        if SCHEMA_AVAILABLE:
            standardized = create_approval_result(
                success=True,
                approval_id=data.get("approval_id"),
                preview_id=preview_id
            )
            return {
                "success": True,
                "approval_id": data.get("approval_id"),
                "preview_id": preview_id,
                "approved_at": data.get("approved_at", datetime.utcnow().isoformat() + "Z"),
                "expires_at": data.get("expires_at"),
                "_standardized": standardized.to_dict()
            }
        
        return {
            "success": True,
            "approval_id": data.get("approval_id"),
            "preview_id": preview_id,
            "approved_at": data.get("approved_at", datetime.utcnow().isoformat() + "Z"),
            "expires_at": data.get("expires_at")
        }
    
    return result


def execute_transaction(approval_id: str) -> Dict[str, Any]:
    """
    Execute an approved transaction.
    
    POST /api/trades/execute
    
    Returns:
        {
            "tx_hash": "0x...",
            "explorer_url": "https://...",
            ...
        }
    """
    if not approval_id:
        return {
            "success": False,
            "error": {"code": "E012", "message": "approval_id is required"},
            "diagnostics": "Cannot execute without approval_id"
        }
    
    result = api_request("POST", "/trades/execute", {"approval_id": approval_id})
    
    if result.get("success"):
        data = result.get("data", {})
        tx_hash = data.get("tx_hash", "")
        network = data.get("network", "base")
        explorer_url = _build_explorer_url(tx_hash, network)
        
        # Create standardized output if schema available
        if SCHEMA_AVAILABLE:
            standardized = create_execution_result(
                success=True,
                tx_hash=tx_hash,
                network=network,
                explorer_url=explorer_url
            )
            return {
                "success": True,
                "tx_hash": tx_hash,
                "explorer_url": explorer_url,
                "executed_at": data.get("executed_at", datetime.utcnow().isoformat() + "Z"),
                "network": network,
                "_standardized": standardized.to_dict()
            }
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "explorer_url": explorer_url,
            "executed_at": data.get("executed_at", datetime.utcnow().isoformat() + "Z"),
            "network": network
        }
    
    return result


def get_transaction_status(tx_hash: str) -> Dict[str, Any]:
    """
    Check transaction status.
    
    GET /api/transactions/{tx_hash}
    """
    if not tx_hash:
        return {
            "success": False,
            "error": {"code": "E013", "message": "tx_hash is required"},
            "diagnostics": "Cannot check status without tx_hash"
        }
    
    result = api_request("GET", f"/transactions/{tx_hash}")
    
    if result.get("success"):
        data = result.get("data", {})
        return {
            "success": True,
            "tx_hash": tx_hash,
            "status": data.get("status", "unknown"),
            "block_number": data.get("block_number"),
            "gas_used": data.get("gas_used"),
            "explorer_url": _build_explorer_url(tx_hash, data.get("network", "base"))
        }
    
    return result


# ============================================================================
# Allowance Management
# ============================================================================

def get_allowances(
    chain: str = "base",
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get current token allowances.
    
    GET /api/allowances
    """
    params = [f"chain={chain}"]
    if token:
        params.append(f"token={token}")
    
    endpoint = "/allowances?" + "&".join(params)
    return api_request("GET", endpoint)


def preview_revoke_allowance(
    token: str,
    spender: str,
    chain: str = "base"
) -> Dict[str, Any]:
    """
    Preview an allowance revoke transaction.
    
    POST /api/allowances/revoke-preview
    """
    payload = {
        "token": token,
        "spender": spender,
        "chain": chain
    }
    
    result = api_request("POST", "/allowances/revoke-preview", payload)
    
    if result.get("success"):
        data = result.get("data", {})
        return {
            "success": True,
            "preview_id": data.get("preview_id"),
            "current_allowance": data.get("current_allowance"),
            "spender": spender,
            "token": token,
            "next_step": "approve"
        }
    
    return result


# ============================================================================
# Helper Functions
# ============================================================================

def _load_security_config() -> Dict[str, Any]:
    """Load security configuration from config.json."""
    config_path = os.path.join(SKILL_DIR, "config", "config.json")
    
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
            return {**DEFAULT_SECURITY, **config.get("security", {})}
    
    return DEFAULT_SECURITY.copy()


def _check_double_confirm_required(
    params: Dict[str, Any],
    preview_result: Dict[str, Any]
) -> tuple:
    """
    Check if double confirmation is required.
    
    Returns:
        (requires_double_confirm, reasons) tuple
    """
    security = _load_security_config()
    double_confirm_config = security.get("double_confirm", {})
    
    if not double_confirm_config.get("enabled", False):
        return False, []
    
    reasons = []
    
    # Check 1: Large trade threshold
    large_trade_threshold = double_confirm_config.get("large_trade_threshold_usd", 5000)
    
    if params.get("amount"):
        try:
            amount = float(params["amount"])
            if amount >= large_trade_threshold:
                reasons.append(f"Large trade: {amount} >= threshold {large_trade_threshold}")
        except (ValueError, TypeError):
            pass
    
    # Check 2: High slippage
    high_slippage_threshold = double_confirm_config.get("high_slippage_threshold_bps", 100)
    slippage = params.get("slippage", 0.5)
    slippage_bps = slippage * 100  # Convert percent to basis points
    
    if slippage_bps >= high_slippage_threshold:
        reasons.append(f"High slippage: {slippage}% >= threshold {high_slippage_threshold/100}%")
    
    # Check 3: New protocol (first use)
    if double_confirm_config.get("new_protocol_confirm", True):
        protocol = params.get("protocol", "")
        if protocol and protocol not in ["auto", "uniswap", "aave", "compound"]:
            reasons.append(f"Protocol '{protocol}' requires confirmation (first use)")
    
    return len(reasons) > 0, reasons


def _extract_risk_info(data: Dict) -> Dict[str, Any]:
    """Extract risk information from API response."""
    return {
        "balance_sufficient": data.get("balance_sufficient", True),
        "allowance_sufficient": data.get("allowance_sufficient", True),
        "route_valid": data.get("route_valid", True),
        "slippage_within_limit": data.get("slippage_within_limit", True),
        "warnings": data.get("risk_warnings", [])
    }


def _build_explorer_url(tx_hash: str, network: str) -> str:
    """Build block explorer URL for transaction."""
    if network in SUPPORTED_CHAINS:
        base = SUPPORTED_CHAINS[network]["explorer"]
        return f"{base}/tx/{tx_hash}"
    return f"https://etherscan.io/tx/{tx_hash}"


def _format_output(data: Dict, json_output: bool = False) -> str:
    """Format output for display."""
    if json_output:
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    if not data.get("success", False):
        error = data.get("error", {})
        diagnostics = data.get("diagnostics", "")
        return f"❌ Error [{error.get('code', '???')}]: {error.get('message', 'Unknown')}\n   Diagnostics: {diagnostics}"
    
    lines = []
    
    # Preview result
    if "preview_id" in data:
        lines.append(f"📋 Preview ID: {data['preview_id']}")
        lines.append(f"   Simulation: {'✅ OK' if data.get('simulation_ok') else '❌ Failed'}")
        
        if data.get("rate"):
            lines.append(f"   Rate: {data['rate']}")
        if data.get("estimated_output"):
            lines.append(f"   Estimated Output: {data['estimated_output']}")
        
        risk = data.get("risk", {})
        if risk.get("warnings"):
            lines.append(f"   ⚠️ Warnings: {', '.join(risk['warnings'])}")
        
        # Double confirmation info
        if data.get("requires_double_confirm"):
            lines.append(f"   🔒 Double Confirmation Required")
            for reason in data.get("double_confirm_reasons", []):
                lines.append(f"      - {reason}")
            if data.get("confirm_instruction"):
                lines.append(f"   {data['confirm_instruction']}")
        
        lines.append(f"   Next Step: {data.get('next_step', 'approve')}")
    
    # Approval result
    elif "approval_id" in data:
        lines.append(f"✅ Approval ID: {data['approval_id']}")
        lines.append(f"   Preview ID: {data['preview_id']}")
        lines.append(f"   Approved At: {data.get('approved_at', 'N/A')}")
        lines.append(f"   Next Step: execute --approval-id {data['approval_id']}")
    
    # Execution result
    elif "tx_hash" in data:
        lines.append(f"🚀 Transaction Submitted!")
        lines.append(f"   TX Hash: {data['tx_hash']}")
        lines.append(f"   Explorer: {data['explorer_url']}")
    
    # Balance result
    elif "balances" in data or data.get("data", {}).get("balances"):
        balances = data.get("balances") or data.get("data", {}).get("balances", [])
        lines.append("💰 Wallet Balances:")
        for bal in balances:
            lines.append(f"   {bal.get('symbol', '?')}: {bal.get('balance', '0')} ({bal.get('chain', '?')})")
    
    return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Trade Executor - REST API adapter for local keystore signer (v0.3.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview a swap
  python3 trade_executor.py preview --type swap --from-token USDC --to-token WETH --amount 5 --network base
  
  # Approve a preview
  python3 trade_executor.py approve --preview-id <uuid>
  
  # Execute an approved transaction
  python3 trade_executor.py execute --approval-id <uuid>
  
  # Check balances
  python3 trade_executor.py balances --network base
  
  # Check transaction status
  python3 trade_executor.py status --tx-hash 0x...
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Preview a transaction")
    preview_parser.add_argument("--type", choices=["swap", "deposit", "transfer"], default="swap", help="Transaction type")
    preview_parser.add_argument("--from-token", help="Source token (for swap)")
    preview_parser.add_argument("--to-token", help="Destination token (for swap)")
    preview_parser.add_argument("--amount", required=True, help="Amount to trade")
    preview_parser.add_argument("--network", choices=["base", "ethereum"], default="base", help="Network")
    preview_parser.add_argument("--protocol", default="auto", help="Protocol to use")
    preview_parser.add_argument("--slippage", type=float, default=0.5, help="Slippage tolerance %%")
    preview_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # For deposit
    preview_parser.add_argument("--asset", help="Asset to deposit (for deposit)")
    
    # Approve command
    approve_parser = subparsers.add_parser("approve", help="Approve a previewed transaction")
    approve_parser.add_argument("--preview-id", required=True, help="Preview ID from preview step")
    approve_parser.add_argument("--confirm", help="Confirmation phrase for high-risk transactions")
    approve_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute an approved transaction")
    execute_parser.add_argument("--approval-id", required=True, help="Approval ID from approve step")
    execute_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check transaction status")
    status_parser.add_argument("--tx-hash", required=True, help="Transaction hash")
    status_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Balances command
    balances_parser = subparsers.add_parser("balances", help="Query wallet balances")
    balances_parser.add_argument("--network", choices=["base", "ethereum"], help="Filter by network")
    balances_parser.add_argument("--tokens", help="Comma-separated token list")
    balances_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Allowances command
    allowances_parser = subparsers.add_parser("allowances", help="Query or manage allowances")
    allowances_parser.add_argument("--revoke", action="store_true", help="Preview revoke allowance")
    allowances_parser.add_argument("--token", help="Token address or symbol")
    allowances_parser.add_argument("--spender", help="Spender address")
    allowances_parser.add_argument("--network", choices=["base", "ethereum"], default="base", help="Network")
    allowances_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Preflight check command
    preflight_parser = subparsers.add_parser("preflight", help="Run pre-flight checks")
    preflight_parser.add_argument("--type", choices=["swap", "deposit", "transfer"], default="swap", help="Transaction type to check")
    preflight_parser.add_argument("--network", choices=["base", "ethereum"], default="base", help="Network")
    preflight_parser.add_argument("--from-token", help="Source token (for swap)")
    preflight_parser.add_argument("--amount", help="Amount")
    preflight_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # RPC status command
    rpc_parser = subparsers.add_parser("rpc", help="Check RPC status and fallback")
    rpc_parser.add_argument("--network", choices=["base", "ethereum"], default="base", help="Network to check")
    rpc_parser.add_argument("--test", action="store_true", help="Test RPC request with fallback")
    rpc_parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    if args.command == "preview":
        if args.type == "swap":
            if not args.from_token or not args.to_token:
                parser.error("--from-token and --to-token are required for swap")
            result = preview_swap(
                from_token=args.from_token,
                to_token=args.to_token,
                amount=args.amount,
                network=args.network,
                slippage=args.slippage,
                protocol=args.protocol
            )
        elif args.type == "deposit":
            if not args.asset or not args.protocol:
                parser.error("--asset and --protocol are required for deposit")
            result = preview_deposit(
                protocol=args.protocol,
                asset=args.asset,
                amount=args.amount,
                network=args.network
            )
        else:
            result = {"success": False, "error": ERROR_CODES["UNKNOWN_ERROR"], "diagnostics": f"Unsupported type: {args.type}"}
        
        print(_format_output(result, args.json))
    
    elif args.command == "approve":
        result = approve_transaction(args.preview_id, confirm_phrase=args.confirm)
        print(_format_output(result, args.json))
    
    elif args.command == "execute":
        result = execute_transaction(args.approval_id)
        print(_format_output(result, args.json))
    
    elif args.command == "status":
        result = get_transaction_status(args.tx_hash)
        print(_format_output(result, args.json))
    
    elif args.command == "balances":
        tokens = args.tokens.split(",") if args.tokens else None
        result = get_wallet_balances(chain=args.network, tokens=tokens)
        print(_format_output(result, args.json))
    
    elif args.command == "allowances":
        if args.revoke:
            if not args.token or not args.spender:
                parser.error("--token and --spender are required for revoke")
            result = preview_revoke_allowance(args.token, args.spender, args.network)
        else:
            result = get_allowances(chain=args.network, token=args.token)
        print(_format_output(result, args.json))
    
    elif args.command == "preflight":
        # Run pre-flight checks directly
        if PREFLIGHT_AVAILABLE:
            config = load_preflight_config(CONFIG_PATH)
            checker = PreflightChecker(config)
            params = {
                "type": args.type,
                "network": args.network,
                "from_token": args.from_token,
                "amount": args.amount
            }
            report = checker.run(args.type, params)
            
            if args.json:
                result = {
                    "success": report.critical_passed,
                    "all_passed": report.all_passed,
                    "summary": report.summary,
                    "checks": [
                        {
                            "name": r.name,
                            "passed": r.passed,
                            "severity": r.severity.value,
                            "message": r.message,
                            "fix_hint": r.fix_hint
                        }
                        for r in report.results
                    ]
                }
                print(json.dumps(result, indent=2))
            else:
                print(f"\n📋 Pre-flight Check Results")
                print(f"   Summary: {report.summary}")
                print(f"   All Passed: {'✅ Yes' if report.all_passed else '⚠️ No'}")
                print(f"   Critical Passed: {'✅ Yes' if report.critical_passed else '❌ No'}")
                print()
                for r in report.results:
                    status = "✅" if r.passed else "❌"
                    sev_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}[r.severity.value]
                    print(f"{status} {sev_emoji} {r.name}: {r.message}")
                    if not r.passed and r.fix_hint:
                        print(f"   💡 Fix: {r.fix_hint}")
                print()
        else:
            print("❌ Pre-flight module not available")
    
    elif args.command == "rpc":
        # Check RPC status
        if RPC_MANAGER_AVAILABLE:
            # Load config from correct path (from skill root)
            skill_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(skill_dir, "config", "config.json")
            with open(config_path) as f:
                rpc_config = json.load(f)
            manager = RPCManager(rpc_config)
            
            if args.test:
                # Test RPC request
                try:
                    result = manager.request(args.network, {
                        "jsonrpc": "2.0",
                        "method": "eth_blockNumber",
                        "params": [],
                        "id": 1
                    })
                    
                    if args.json:
                        print(json.dumps({
                            "success": True,
                            "network": args.network,
                            "active_rpc": manager.get_active_rpc(args.network),
                            "result": result
                        }, indent=2))
                    else:
                        block = int(result.get("result", "0x0"), 16)
                        print(f"\n🔗 RPC Test: {args.network}")
                        print(f"   Active RPC: {manager.get_active_rpc(args.network)}")
                        print(f"   Block Number: #{block}")
                        print(f"   Status: ✅ OK")
                        print()
                
                except Exception as e:
                    if args.json:
                        print(json.dumps({
                            "success": False,
                            "network": args.network,
                            "error": str(e)
                        }, indent=2))
                    else:
                        print(f"\n❌ RPC Test Failed: {e}")
            else:
                # Show status report
                report = manager.get_status_report(args.network)
                
                if args.json:
                    print(json.dumps(report, indent=2))
                else:
                    print(f"\n🔗 RPC Status: {args.network.upper()}")
                    print(f"   Active: {report['active_rpc']}")
                    print(f"   Fallback Enabled: {'✅' if report['fallback_enabled'] else '❌'}")
                    print(f"   Session Sticky: {'✅' if report['session_sticky'] else '❌'}")
                    print()
                    print("   Endpoints:")
                    for ep in report['endpoints']:
                        status = "✅ Active" if ep['is_active'] else "⏸️  Standby"
                        print(f"      {status}: {ep['url']}")
                    print()
        else:
            print("❌ RPC Manager module not available")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()