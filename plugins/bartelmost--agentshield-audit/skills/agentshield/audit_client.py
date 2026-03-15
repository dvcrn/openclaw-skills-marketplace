#!/usr/bin/env python3
"""
Low-level AgentShield API client.
"""

import base64
import json
import os
import requests
from typing import Optional, Dict, Any

AGENTSHIELD_API = os.environ.get("AGENTSHIELD_API", "https://agentshield.live")


class AgentShieldClient:
    """Client for AgentShield Audit API."""
    
    def __init__(self, api_url: str = None):
        self.api_url = api_url or AGENTSHIELD_API
        self.session = requests.Session()
    
    def initiate_audit(
        self,
        agent_name: str,
        platform: str,
        public_key: str,
        agent_version: str = None
    ) -> Dict[str, Any]:
        """
        Initiate a new audit session.
        
        Args:
            agent_name: Human-readable agent name
            platform: Platform identifier (telegram, discord, etc.)
            public_key: Base64-encoded Ed25519 public key
            agent_version: Optional version string
        
        Returns:
            Audit session info including challenge
        """
        payload = {
            "agent_name": agent_name,
            "platform": platform,
            "public_key": public_key
        }
        if agent_version:
            payload["agent_version"] = agent_version
        
        response = self.session.post(
            f"{self.api_url}/api/agent-audit/initiate",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def complete_challenge(
        self,
        audit_id: str,
        challenge_response: str
    ) -> Dict[str, Any]:
        """
        Complete challenge-response authentication.
        
        Args:
            audit_id: Audit session ID
            challenge_response: Base64-encoded signature of challenge
        
        Returns:
            Authentication result
        """
        payload = {
            "audit_id": audit_id,
            "challenge_response": challenge_response
        }
        
        response = self.session.post(
            f"{self.api_url}/api/agent-audit/challenge",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def submit_results(
        self,
        audit_id: str,
        test_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit test results and receive certificate.
        
        Args:
            audit_id: Audit session ID
            test_results: Results from security tests
        
        Returns:
            Certificate data
        """
        payload = {
            "audit_id": audit_id,
            "test_results": test_results
        }
        
        response = self.session.post(
            f"{self.api_url}/api/agent-audit/complete",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def verify_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Verify an agent's certificate.
        
        Args:
            agent_id: Agent's unique identifier
        
        Returns:
            Certificate data or error
        """
        response = self.session.get(
            f"{self.api_url}/api/verify/{agent_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def revoke_certificate(
        self,
        agent_id: str,
        reason: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Revoke a certificate (requires agent's signature).
        
        Args:
            agent_id: Agent to revoke
            reason: Revocation reason
            signature: Signature of revocation request
        
        Returns:
            Revocation confirmation
        """
        payload = {
            "agent_id": agent_id,
            "reason": reason,
            "signature": signature
        }
        
        response = self.session.post(
            f"{self.api_url}/api/agent-audit/revoke",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> bool:
        """Check if API is available."""
        try:
            response = self.session.get(
                f"{self.api_url}/api/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


def main():
    """CLI for API client."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AgentShield API Client")
    parser.add_argument("--api-url", help="Override API URL")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Health check
    subparsers.add_parser("health", help="Check API health")
    
    # Verify
    verify_parser = subparsers.add_parser("verify", help="Verify an agent")
    verify_parser.add_argument("agent-id", help="Agent ID to verify")
    
    args = parser.parse_args()
    
    client = AgentShieldClient(args.api_url)
    
    if args.command == "health":
        if client.health_check():
            print("✅ AgentShield API is online")
        else:
            print("❌ AgentShield API is unreachable")
            exit(1)
    
    elif args.command == "verify":
        agent_id = getattr(args, 'agent-id')
        try:
            result = client.verify_agent(agent_id)
            print(json.dumps(result, indent=2))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"❌ Agent {agent_id} not found")
            else:
                print(f"❌ Error: {e}")
            exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
