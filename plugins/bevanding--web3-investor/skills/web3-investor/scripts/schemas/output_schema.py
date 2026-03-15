"""
Output Schema Module

Provides standardized output formats for all transaction operations.
Inspired by xaut-trade's structured output design.

Key Features:
- Consistent structure across swap/transfer/deposit operations
- Clear stage indication (preview/ready_to_execute)
- Risk warnings and confirmation requirements
- Machine-readable JSON and human-readable text output
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid
import json


class Stage(str, Enum):
    """Transaction stage."""
    PREVIEW = "preview"
    READY_TO_EXECUTE = "ready_to_execute"
    EXECUTED = "executed"
    FAILED = "failed"


class RiskLevel(str, Enum):
    """Risk severity level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class RiskWarning:
    """Risk warning item."""
    type: str
    level: RiskLevel
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class InputInfo:
    """Transaction input information."""
    token: str
    amount: str
    chain: str
    token_out: Optional[str] = None  # For swap
    protocol: Optional[str] = None   # For deposit


@dataclass
class QuoteInfo:
    """Quote information (varies by transaction type)."""
    estimated_output: Optional[str] = None
    rate: Optional[str] = None
    slippage_bps: Optional[int] = None
    min_amount_out: Optional[str] = None
    gas_estimate: Optional[str] = None
    apy: Optional[str] = None  # For deposit/staking


@dataclass
class PreviewOutput:
    """
    Standardized preview output format.
    
    Used for all transaction types: swap, transfer, deposit.
    """
    stage: Stage
    request_id: str
    timestamp: str
    
    # Input
    input: InputInfo
    
    # Quote (varies by type)
    quote: QuoteInfo
    
    # Risk warnings
    risk_warnings: List[RiskWarning]
    
    # Confirmation
    requires_double_confirm: bool = False
    double_confirm_reasons: List[str] = field(default_factory=list)
    confirm_instruction: Optional[str] = None
    
    # Navigation
    next_step: str = "approve"
    
    # Raw data (for debugging)
    raw_preview_id: Optional[str] = None
    raw_transaction: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "stage": self.stage.value,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "input": asdict(self.input),
            "quote": asdict(self.quote),
            "risk_warnings": [
                {
                    "type": w.type,
                    "level": w.level.value,
                    "message": w.message,
                    **({"details": w.details} if w.details else {})
                }
                for w in self.risk_warnings
            ],
            "requires_double_confirm": self.requires_double_confirm,
            "next_step": self.next_step
        }
        
        if self.requires_double_confirm:
            result["double_confirm_reasons"] = self.double_confirm_reasons
            if self.confirm_instruction:
                result["confirm_instruction"] = self.confirm_instruction
        
        if self.raw_preview_id:
            result["preview_id"] = self.raw_preview_id
        
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_text(self) -> str:
        """Convert to human-readable text."""
        lines = []
        
        # Header
        lines.append(f"📋 Preview ID: {self.raw_preview_id or self.request_id}")
        lines.append(f"   Stage: {self.stage.value}")
        lines.append("")
        
        # Input
        lines.append("   Input:")
        lines.append(f"      Token: {self.input.token}")
        lines.append(f"      Amount: {self.input.amount}")
        lines.append(f"      Chain: {self.input.chain}")
        if self.input.token_out:
            lines.append(f"      → Output: {self.input.token_out}")
        if self.input.protocol:
            lines.append(f"      Protocol: {self.input.protocol}")
        lines.append("")
        
        # Quote
        if self.quote.estimated_output or self.quote.rate:
            lines.append("   Quote:")
            if self.quote.rate:
                lines.append(f"      Rate: {self.quote.rate}")
            if self.quote.estimated_output:
                lines.append(f"      Estimated Output: {self.quote.estimated_output}")
            if self.quote.slippage_bps:
                lines.append(f"      Slippage: {self.quote.slippage_bps} bps")
            if self.quote.min_amount_out:
                lines.append(f"      Min Output: {self.quote.min_amount_out}")
            if self.quote.gas_estimate:
                lines.append(f"      Gas Estimate: {self.quote.gas_estimate}")
            if self.quote.apy:
                lines.append(f"      APY: {self.quote.apy}")
            lines.append("")
        
        # Risk warnings
        if self.risk_warnings:
            lines.append("   ⚠️ Risk Warnings:")
            for w in self.risk_warnings:
                level_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}[w.level.value]
                lines.append(f"      {level_emoji} {w.type}: {w.message}")
            lines.append("")
        
        # Double confirm
        if self.requires_double_confirm:
            lines.append("   🔒 Double Confirmation Required:")
            for reason in self.double_confirm_reasons:
                lines.append(f"      - {reason}")
            if self.confirm_instruction:
                lines.append(f"   {self.confirm_instruction}")
            lines.append("")
        
        # Next step
        lines.append(f"   Next Step: {self.next_step}")
        
        return "\n".join(lines)


@dataclass
class ApprovalResult:
    """Standardized approval result."""
    success: bool
    approval_id: Optional[str] = None
    preview_id: Optional[str] = None
    approved_at: Optional[str] = None
    expires_at: Optional[str] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "success": self.success,
            "approval_id": self.approval_id,
            "preview_id": self.preview_id,
            "approved_at": self.approved_at
        }
        
        if self.expires_at:
            result["expires_at"] = self.expires_at
        
        if self.error:
            result["error"] = self.error
        
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_text(self) -> str:
        """Convert to human-readable text."""
        if self.success:
            lines = [
                f"✅ Approval ID: {self.approval_id}",
                f"   Preview ID: {self.preview_id}",
                f"   Approved At: {self.approved_at}",
                f"   Next Step: execute --approval-id {self.approval_id}"
            ]
        else:
            error = self.error or {}
            lines = [
                f"❌ Approval Failed",
                f"   Error: {error.get('message', 'Unknown')}"
            ]
        
        return "\n".join(lines)


@dataclass
class ExecutionResult:
    """Standardized execution result."""
    success: bool
    tx_hash: Optional[str] = None
    explorer_url: Optional[str] = None
    network: Optional[str] = None
    executed_at: Optional[str] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "success": self.success,
            "tx_hash": self.tx_hash,
            "network": self.network,
            "executed_at": self.executed_at
        }
        
        if self.explorer_url:
            result["explorer_url"] = self.explorer_url
        
        if self.error:
            result["error"] = self.error
        
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_text(self) -> str:
        """Convert to human-readable text."""
        if self.success:
            lines = [
                "🚀 Transaction Submitted!",
                f"   TX Hash: {self.tx_hash}",
                f"   Network: {self.network}",
                f"   Explorer: {self.explorer_url}"
            ]
        else:
            error = self.error or {}
            lines = [
                "❌ Execution Failed",
                f"   Error: {error.get('message', 'Unknown')}"
            ]
        
        return "\n".join(lines)


# Factory functions

def create_preview_output(
    input_info: InputInfo,
    quote_info: QuoteInfo,
    risk_warnings: List[RiskWarning],
    requires_double_confirm: bool = False,
    double_confirm_reasons: List[str] = None,
    confirm_instruction: str = None,
    preview_id: str = None,
    raw_transaction: Dict = None
) -> PreviewOutput:
    """Create a standardized preview output."""
    return PreviewOutput(
        stage=Stage.PREVIEW,
        request_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat() + "Z",
        input=input_info,
        quote=quote_info,
        risk_warnings=risk_warnings,
        requires_double_confirm=requires_double_confirm,
        double_confirm_reasons=double_confirm_reasons or [],
        confirm_instruction=confirm_instruction,
        next_step="approve",
        raw_preview_id=preview_id,
        raw_transaction=raw_transaction
    )


def create_approval_result(
    success: bool,
    approval_id: str = None,
    preview_id: str = None,
    error: Dict = None
) -> ApprovalResult:
    """Create a standardized approval result."""
    return ApprovalResult(
        success=success,
        approval_id=approval_id,
        preview_id=preview_id,
        approved_at=datetime.utcnow().isoformat() + "Z" if success else None,
        error=error
    )


def create_execution_result(
    success: bool,
    tx_hash: str = None,
    network: str = None,
    explorer_url: str = None,
    error: Dict = None
) -> ExecutionResult:
    """Create a standardized execution result."""
    return ExecutionResult(
        success=success,
        tx_hash=tx_hash,
        network=network,
        explorer_url=explorer_url,
        executed_at=datetime.utcnow().isoformat() + "Z" if success else None,
        error=error
    )


if __name__ == "__main__":
    # Test output
    preview = create_preview_output(
        input_info=InputInfo(
            token="USDC",
            amount="10000",
            chain="base",
            token_out="WETH"
        ),
        quote_info=QuoteInfo(
            estimated_output="5.0",
            rate="1 WETH = 2000 USDC",
            slippage_bps=50,
            min_amount_out="4.975"
        ),
        risk_warnings=[
            RiskWarning(
                type="large_trade",
                level=RiskLevel.MEDIUM,
                message="Large trade size, consider price impact"
            )
        ],
        requires_double_confirm=True,
        double_confirm_reasons=["Large trade: 10000 >= threshold 5000"],
        confirm_instruction='To approve, use: --confirm "CONFIRM_HIGH_RISK"',
        preview_id="test-preview-id-123"
    )
    
    print("=== JSON Output ===")
    print(preview.to_json())
    
    print("\n=== Text Output ===")
    print(preview.to_text())