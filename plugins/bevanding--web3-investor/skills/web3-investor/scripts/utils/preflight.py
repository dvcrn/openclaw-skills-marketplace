"""
Pre-flight Checks Module

Provides environment validation before executing transactions.
Supports multiple check types that can be configured per transaction type.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urljoin

try:
    from .rpc_manager import RPCManager
    RPC_MANAGER_AVAILABLE = True
except ImportError:
    try:
        from utils.rpc_manager import RPCManager
        RPC_MANAGER_AVAILABLE = True
    except ImportError:
        RPC_MANAGER_AVAILABLE = False


class CheckSeverity(Enum):
    """Severity levels for check results."""
    CRITICAL = "critical"      # Hard stop, cannot proceed
    WARNING = "warning"        # Warning, can proceed with caution
    INFO = "info"              # Informational only


@dataclass
class CheckResult:
    """Result of a single pre-flight check."""
    name: str
    passed: bool
    severity: CheckSeverity
    message: str
    fix_hint: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreflightReport:
    """Complete pre-flight check report."""
    all_passed: bool
    critical_passed: bool
    results: List[CheckResult]
    summary: str = ""


class PreflightChecker:
    """
    Pre-flight checker for transaction execution.
    
    Usage:
        checker = PreflightChecker(config)
        report = checker.run(transaction_type="swap", params={...})
        if not report.all_passed:
            raise PreflightError(report)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.checks_registry = self._build_checks_registry()
    
    def _build_checks_registry(self) -> Dict[str, Callable]:
        """Build registry of available check functions."""
        return {
            "signer_api": self._check_signer_api,
            "rpc_reachable": self._check_rpc_reachable,
            "gas_balance": self._check_gas_balance,
            "token_balance": self._check_token_balance,
        }
    
    def run(
        self,
        transaction_type: str,
        params: Optional[Dict[str, Any]] = None
    ) -> PreflightReport:
        """
        Run pre-flight checks for a transaction.
        
        Args:
            transaction_type: Type of transaction (swap, transfer, deposit, etc.)
            params: Transaction parameters (token, amount, network, etc.)
        
        Returns:
            PreflightReport with all check results
        """
        params = params or {}
        
        # Get check list for this transaction type from config
        check_list = self._get_check_list(transaction_type)
        
        results = []
        for check_name in check_list:
            check_fn = self.checks_registry.get(check_name)
            if check_fn:
                try:
                    result = check_fn(params)
                except Exception as e:
                    result = CheckResult(
                        name=check_name,
                        passed=False,
                        severity=CheckSeverity.CRITICAL,
                        message=f"Check failed with exception: {str(e)}",
                        fix_hint="Check logs for details"
                    )
                results.append(result)
        
        # Determine overall status
        critical_results = [r for r in results if r.severity == CheckSeverity.CRITICAL]
        critical_passed = all(r.passed for r in critical_results)
        all_passed = all(r.passed for r in results)
        
        summary = self._build_summary(results, critical_passed)
        
        return PreflightReport(
            all_passed=all_passed,
            critical_passed=critical_passed,
            results=results,
            summary=summary
        )
    
    def _get_check_list(self, transaction_type: str) -> List[str]:
        """Get list of checks to run for a transaction type."""
        preflight_config = self.config.get("preflight", {})
        
        # Get checks for this specific type
        checks_config = preflight_config.get("checks", {})
        type_checks = checks_config.get(transaction_type)
        if type_checks:
            return type_checks
        
        # Fall back to swap checks
        return checks_config.get("swap", ["api", "rpc"])
    
    def _build_summary(self, results: List[CheckResult], critical_passed: bool) -> str:
        """Build human-readable summary of check results."""
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        
        if critical_passed:
            return f"Pre-flight checks: {passed}/{total} passed"
        
        failed_critical = [r for r in results if not r.passed and r.severity == CheckSeverity.CRITICAL]
        failed_names = ", ".join(r.name for r in failed_critical)
        return f"Pre-flight checks failed: {failed_names}"
    
    # ==================== Individual Check Functions ====================
    
    def _check_signer_api(self, params: Dict[str, Any]) -> CheckResult:
        """Check if signer API is reachable."""
        # Support both old and new config paths
        api_config = self.config.get("api", {})
        api_url = api_config.get("url") or api_config.get("url", "")
        timeout = api_config.get("timeout_seconds", 30)
        
        # Handle environment variable syntax ${VAR:default}
        if api_url and api_url.startswith("${"):
            import os
            import re
            match = re.match(r'\$\{([^:}]+):?(.*?)\}', api_url)
            if match:
                env_var = match.group(1)
                default = match.group(2)
                api_url = os.environ.get(env_var, default)
        
        if not api_url:
            return CheckResult(
                name="signer_api",
                passed=False,
                severity=CheckSeverity.CRITICAL,
                message="API URL not configured",
                fix_hint="Set WEB3_INVESTOR_API_URL environment variable or update config.json"
            )
        
        try:
            # Try to call health check or balances endpoint
            health_url = urljoin(api_url, "/wallet/balances")
            response = requests.get(health_url, timeout=timeout)
            
            if response.status_code in [200, 401]:  # 401 is OK (auth required but service up)
                return CheckResult(
                    name="signer_api",
                    passed=True,
                    severity=CheckSeverity.CRITICAL,
                    message="Signer API is reachable",
                    details={"url": api_url, "status": response.status_code}
                )
            else:
                return CheckResult(
                    name="signer_api",
                    passed=False,
                    severity=CheckSeverity.CRITICAL,
                    message=f"Signer API returned unexpected status: {response.status_code}",
                    fix_hint="Check signer service status"
                )
        
        except requests.exceptions.ConnectionError:
            return CheckResult(
                name="signer_api",
                passed=False,
                severity=CheckSeverity.CRITICAL,
                message="Cannot connect to signer API",
                fix_hint="Ensure signer service is running on the configured port"
            )
        except requests.exceptions.Timeout:
            return CheckResult(
                name="signer_api",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Signer API connection timed out",
                fix_hint="Check network connectivity or increase timeout in config"
            )
        except Exception as e:
            return CheckResult(
                name="signer_api",
                passed=False,
                severity=CheckSeverity.CRITICAL,
                message=f"Unexpected error checking signer API: {str(e)}",
                fix_hint="Check configuration and network"
            )
    
    def _check_rpc_reachable(self, params: Dict[str, Any]) -> CheckResult:
        """Check if RPC endpoint is reachable (with fallback support)."""
        network = params.get("network", self.config.get("discovery", {}).get("default_chain", "base"))
        
        # Try using RPC Manager for fallback support
        if RPC_MANAGER_AVAILABLE:
            try:
                manager = RPCManager(self.config)
                url = manager.get_active_rpc(network)
                
                if not url:
                    return CheckResult(
                        name="rpc_reachable",
                        passed=False,
                        severity=CheckSeverity.CRITICAL,
                        message=f"No RPC endpoint configured for network: {network}",
                        fix_hint=f"Add RPC endpoint for {network} in config.json"
                    )
                
                success, block_number = manager.health_check(network, url)
                
                if success:
                    return CheckResult(
                        name="rpc_reachable",
                        passed=True,
                        severity=CheckSeverity.CRITICAL,
                        message=f"RPC reachable (block #{block_number})",
                        details={"rpc_url": url, "block_number": block_number, "fallback_available": manager.rpc_config.get("fallback_enabled", False)}
                    )
                
                # Primary failed, try fallback
                if manager.rpc_config.get("fallback_enabled", False):
                    fallback_url = manager.find_healthy_fallback(network)
                    if fallback_url:
                        success, block_number = manager.health_check(network, fallback_url)
                        if success:
                            return CheckResult(
                                name="rpc_reachable",
                                passed=True,
                                severity=CheckSeverity.WARNING,
                                message=f"RPC reachable via fallback (block #{block_number})",
                                details={"rpc_url": fallback_url, "block_number": block_number, "original_failed": url}
                            )
                
                return CheckResult(
                    name="rpc_reachable",
                    passed=False,
                    severity=CheckSeverity.CRITICAL,
                    message=f"RPC unreachable: {url}",
                    fix_hint="Check RPC URL or configure fallback RPCs in config.json"
                )
            
            except Exception as e:
                return CheckResult(
                    name="rpc_reachable",
                    passed=False,
                    severity=CheckSeverity.CRITICAL,
                    message=f"RPC check failed: {str(e)}",
                    fix_hint="Check RPC configuration"
                )
        
        # Fallback: direct check without RPC Manager
        rpc_config = self.config.get("rpc", {})
        rpc_urls = rpc_config.get("endpoints", {}).get(network, [])
        
        if not rpc_urls:
            return CheckResult(
                name="rpc_reachable",
                passed=False,
                severity=CheckSeverity.CRITICAL,
                message=f"No RPC endpoint configured for network: {network}",
                fix_hint=f"Add RPC endpoint for {network} in config.json"
            )
        
        primary_rpc = rpc_urls[0]
        timeout = rpc_config.get("timeout_seconds", 10)
        
        try:
            response = requests.post(
                primary_rpc,
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
                    return CheckResult(
                        name="rpc_reachable",
                        passed=True,
                        severity=CheckSeverity.CRITICAL,
                        message=f"RPC reachable (block #{block_number})",
                        details={"rpc_url": primary_rpc, "block_number": block_number}
                    )
            
            return CheckResult(
                name="rpc_reachable",
                passed=False,
                severity=CheckSeverity.CRITICAL,
                message=f"RPC returned unexpected response: {response.status_code}",
                fix_hint="Check RPC URL and network connectivity"
            )
        
        except requests.exceptions.RequestException as e:
            return CheckResult(
                name="rpc_reachable",
                passed=False,
                severity=CheckSeverity.CRITICAL,
                message=f"Cannot connect to RPC: {str(e)}",
                fix_hint="Check RPC URL or configure fallback RPCs"
            )
    
    def _check_env_completeness(self, params: Dict[str, Any]) -> CheckResult:
        """Check if required environment variables are set."""
        preflight_config = self.config.get("preflight", {})
        required_vars = preflight_config.get("required_env_vars", [])
        
        missing = []
        for var in required_vars:
            if not os.environ.get(var):
                missing.append(var)
        
        if missing:
            return CheckResult(
                name="env_completeness",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"Missing environment variables: {', '.join(missing)}",
                fix_hint="Add missing variables to ~/.bashrc or .env file"
            )
        
        return CheckResult(
            name="env_completeness",
            passed=True,
            severity=CheckSeverity.INFO,
            message="All required environment variables present"
        )
    
    def _check_gas_balance(self, params: Dict[str, Any]) -> CheckResult:
        """Check if wallet has sufficient gas balance."""
        # This check requires the signer API to be available
        # It will be skipped if signer API is not reachable
        api_url = self.config.get("api", {}).get("url", "")
        network = params.get("network", "base")
        
        if not api_url:
            return CheckResult(
                name="gas_balance",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Cannot check gas balance: API URL not configured",
                fix_hint="Configure API base URL"
            )
        
        try:
            # Get native token balance (ETH for ethereum, ETH for base)
            response = requests.get(
                f"{api_url}/wallet/balances?chain={network}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                balances = data.get("balances", [])
                
                # Find native token (ETH)
                native_balance = None
                for bal in balances:
                    if bal.get("symbol") in ["ETH", "WETH"]:
                        native_balance = float(bal.get("balance", 0))
                        break
                
                min_gas = self.config.get("preflight", {}).get("min_gas_balance_eth", 0.001)
                
                if native_balance is None or native_balance < min_gas:
                    return CheckResult(
                        name="gas_balance",
                        passed=False,
                        severity=CheckSeverity.CRITICAL,
                        message=f"Insufficient gas balance: {native_balance or 0} ETH (min: {min_gas})",
                        fix_hint=f"Top up wallet with at least {min_gas} ETH for gas fees"
                    )
                
                return CheckResult(
                    name="gas_balance",
                    passed=True,
                    severity=CheckSeverity.CRITICAL,
                    message=f"Gas balance sufficient: {native_balance} ETH",
                    details={"balance_eth": native_balance, "min_required": min_gas}
                )
            
            return CheckResult(
                name="gas_balance",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Could not fetch gas balance from API",
                fix_hint="Check API connectivity"
            )
        
        except Exception as e:
            return CheckResult(
                name="gas_balance",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"Error checking gas balance: {str(e)}",
                fix_hint="Check API status"
            )
    
    def _check_token_balance(self, params: Dict[str, Any]) -> CheckResult:
        """Check if wallet has sufficient token balance for transaction."""
        token = params.get("from_token") or params.get("asset")
        amount = params.get("amount")
        network = params.get("network", "base")
        
        if not token or not amount:
            return CheckResult(
                name="token_balance",
                passed=True,
                severity=CheckSeverity.INFO,
                message="Token balance check skipped: token or amount not specified",
                details={"token": token, "amount": amount}
            )
        
        api_url = self.config.get("api", {}).get("url", "")
        
        try:
            response = requests.get(
                f"{api_url}/wallet/balances?chain={network}&tokens={token}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                balances = data.get("balances", [])
                
                token_balance = None
                for bal in balances:
                    if bal.get("symbol", "").upper() == token.upper():
                        token_balance = float(bal.get("balance", 0))
                        break
                
                amount_float = float(amount)
                
                if token_balance is None or token_balance < amount_float:
                    return CheckResult(
                        name="token_balance",
                        passed=False,
                        severity=CheckSeverity.CRITICAL,
                        message=f"Insufficient {token} balance: {token_balance or 0} (required: {amount})",
                        fix_hint=f"Deposit {amount} {token} to wallet before proceeding"
                    )
                
                return CheckResult(
                    name="token_balance",
                    passed=True,
                    severity=CheckSeverity.CRITICAL,
                    message=f"Token balance sufficient: {token_balance} {token}",
                    details={"token": token, "balance": token_balance, "required": amount_float}
                )
            
            return CheckResult(
                name="token_balance",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Could not fetch token balance from API",
                fix_hint="Check API connectivity"
            )
        
        except Exception as e:
            return CheckResult(
                name="token_balance",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"Error checking token balance: {str(e)}",
                fix_hint="Check API status"
            )
    
    def _check_allowance(self, params: Dict[str, Any]) -> CheckResult:
        """Check if token allowance is sufficient (for swap/deposit only)."""
        tx_type = params.get("type", "")
        
        # Allowance check only relevant for swap and deposit
        if tx_type not in ["swap", "deposit"]:
            return CheckResult(
                name="allowance",
                passed=True,
                severity=CheckSeverity.INFO,
                message="Allowance check not required for this transaction type"
            )
        
        # This is a soft check - actual allowance will be checked during preview
        return CheckResult(
            name="allowance",
            passed=True,
            severity=CheckSeverity.INFO,
            message="Allowance will be checked during transaction preview"
        )


class PreflightError(Exception):
    """Exception raised when pre-flight checks fail."""
    
    def __init__(self, report: PreflightReport):
        self.report = report
        self.message = report.summary
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses."""
        return {
            "success": False,
            "error": {
                "code": "E014",
                "message": "Pre-flight checks failed",
                "details": {
                    "summary": self.report.summary,
                    "failed_checks": [
                        {
                            "name": r.name,
                            "message": r.message,
                            "fix_hint": r.fix_hint,
                            "severity": r.severity.value
                        }
                        for r in self.report.results if not r.passed
                    ]
                }
            }
        }


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from config.json."""
    if config_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        skill_dir = os.path.dirname(os.path.dirname(script_dir))  # utils -> scripts -> skill_dir
        config_path = os.path.join(skill_dir, "config", "config.json")
    
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    
    return {}


if __name__ == "__main__":
    # Simple test
    config = load_config()
    checker = PreflightChecker(config)
    report = checker.run("swap", {"network": "base", "from_token": "USDC", "amount": "100"})
    print(f"All passed: {report.all_passed}")
    print(f"Summary: {report.summary}")
    for r in report.results:
        status = "✅" if r.passed else "❌"
        print(f"{status} {r.name}: {r.message}")
