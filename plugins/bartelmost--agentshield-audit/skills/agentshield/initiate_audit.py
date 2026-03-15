#!/usr/bin/env python3
"""
AgentShield Audit Initiation
Generates keypair, authenticates with AgentShield, runs security audit.

Now with auto-detection capabilities!
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# AgentShield API endpoint
AGENTSHIELD_API = os.environ.get("AGENTSHIELD_API", "https://agentshield.live")

# Local storage paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
AGENTSHIELD_DIR = WORKSPACE / ".agentshield"
KEY_FILE = AGENTSHIELD_DIR / "agent.key"
CERT_FILE = AGENTSHIELD_DIR / "certificate.json"
CONFIG_FILE = AGENTSHIELD_DIR / "config.json"

# Files to check for agent name detection
IDENTITY_FILES = [
    WORKSPACE / "IDENTITY.md",
    WORKSPACE / "SOUL.md", 
    WORKSPACE / "AGENTS.md",
]


def ensure_directory():
    """Create .agentshield directory if needed."""
    AGENTSHIELD_DIR.mkdir(parents=True, exist_ok=True)


def detect_agent_name():
    """
    Auto-detect agent name from identity files.
    Checks: IDENTITY.md, SOUL.md, AGENTS.md
    Returns: (name, confidence) tuple
    """
    name_patterns = [
        r'(?:^|\n)[\s]*[-*]?[\s]*(?:Name|name)[\s]*[:\-]?\s*["\']?([^\n"\']+)["\']?',
        r'(?:^|\n)[\s]*#+\s*(?:I am|Name is|About)[\s:]+([^\n]+)',
    ]
    
    for file_path in IDENTITY_FILES:
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            for pattern in name_patterns:
                match = re.search(pattern, content)
                if match:
                    name = match.group(1).strip()
                    # Clean up the name
                    name = re.sub(r'[\*\-\#\`]', '', name).strip()
                    if len(name) > 1 and len(name) < 50:
                        return name, 0.9
        except Exception:
            continue
    
    # Fallback: try to get from environment
    env_name = os.environ.get('AGENT_NAME') or os.environ.get('OPENCLAW_AGENT_NAME')
    if env_name:
        return env_name, 0.7
    
    return None, 0.0


def detect_platform():
    """
    Auto-detect platform/channel from config files only.
    Does NOT scan environment variables (privacy-first design).
    Returns: (platform, confidence) tuple
    """
    # NOTE: Previously checked environment variables like TELEGRAM_TOKEN,
    # DISCORD_TOKEN, etc. This has been removed for privacy reasons.
    # We only check config files now.
    
    # Check channel config file if exists
    channel_file = WORKSPACE / ".channel" / "config.json"
    if channel_file.exists():
        try:
            with open(channel_file) as f:
                config = json.load(f)
            channel = config.get('channel', '').lower()
            if channel:
                return channel, 0.9
        except Exception:
            pass
    
    # Default - no env var scanning for privacy
    return "openclaw", 0.5


def detect_platform_from_args(args_platform: str = None) -> tuple:
    """
    Get platform from explicit arguments only.
    Fallback to config file. Never scans environment variables.
    """
    if args_platform and args_platform != "openclaw":
        return args_platform, 1.0
    
    # Try config file
    channel_file = WORKSPACE / ".channel" / "config.json"
    if channel_file.exists():
        try:
            with open(channel_file) as f:
                config = json.load(f)
            channel = config.get('channel', '').lower()
            if channel:
                return channel, 0.9
        except Exception:
            pass
    
    return "openclaw", 0.5


def detect_openclaw_version():
    """
    Detect OpenClaw version.
    Returns: version string or None
    """
    # Try running openclaw command
    try:
        result = subprocess.run(
            ['openclaw', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            if version:
                return version
    except Exception:
        pass
    
    # Check config file
    config_file = Path.home() / ".openclaw" / "openclaw.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
            version = config.get('version')
            if version:
                return f"openclaw-{version}"
        except Exception:
            pass
    
    return None


def auto_detect_all():
    """
    Auto-detect all agent information.
    Returns: dict with name, platform, version and confidence scores
    """
    name, name_conf = detect_agent_name()
    platform, platform_conf = detect_platform()
    version = detect_openclaw_version()
    
    overall_confidence = (name_conf + platform_conf) / 2
    
    return {
        'name': name,
        'name_confidence': name_conf,
        'platform': platform,
        'platform_confidence': platform_conf,
        'version': version,
        'overall_confidence': overall_confidence
    }


def generate_keypair():
    """Generate Ed25519 keypair for agent identity."""
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Serialize keys
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        return {
            'private_key': base64.b64encode(private_bytes).decode('utf-8'),
            'public_key': base64.b64encode(public_bytes).decode('utf-8')
        }
    except ImportError:
        print("Error: cryptography library required. Install: pip install cryptography")
        sys.exit(1)


def load_or_create_keys():
    """Load existing keys or generate new ones."""
    ensure_directory()
    
    if KEY_FILE.exists():
        with open(KEY_FILE, 'r') as f:
            return json.load(f)
    
    # Generate new keys
    keys = generate_keypair()
    with open(KEY_FILE, 'w') as f:
        json.dump(keys, f, indent=2)
    # Restrict permissions
    os.chmod(KEY_FILE, 0o600)
    print(f"✓ Generated new agent identity")
    return keys


def sign_challenge(private_key_b64: str, challenge: str) -> str:
    """Sign challenge with private key."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    
    private_bytes = base64.b64decode(private_key_b64)
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
    
    signature = private_key.sign(challenge.encode('utf-8'))
    return base64.b64encode(signature).decode('utf-8')


def initiate_audit(agent_name: str, platform: str, agent_version: str = None) -> dict:
    """
    Initiate audit with AgentShield API.
    Returns audit session info.
    """
    import requests
    
    keys = load_or_create_keys()
    
    # Build request payload
    payload = {
        "agent_name": agent_name,
        "platform": platform,
        "public_key": keys['public_key'],
    }
    
    if agent_version:
        payload["agent_version"] = agent_version
    
    try:
        response = requests.post(
            f"{AGENTSHIELD_API}/api/agent-audit/initiate",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to AgentShield API at {AGENTSHIELD_API}")
        print("Please check your internet connection and try again.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: API returned error: {e}")
        try:
            error_data = response.json()
            print(f"Details: {error_data.get('error', 'Unknown error')}")
        except:
            pass
        sys.exit(1)


def complete_challenge(audit_id: str, challenge: str, private_key: str) -> dict:
    """Complete challenge-response authentication."""
    import requests
    
    signature = sign_challenge(private_key, challenge)
    
    payload = {
        "audit_id": audit_id,
        "challenge_response": signature
    }
    
    response = requests.post(
        f"{AGENTSHIELD_API}/api/agent-audit/challenge",
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def run_security_tests(audit_id: str) -> dict:
    """
    Run 77 security tests using AgentShieldSecurityTester.
    Returns test_results dict.
    """
    print("Running 77 security tests...")
    
    # Import the full test suite
    try:
        from agentshield_tester import AgentShieldSecurityTester
    except ImportError:
        # If agentshield_tester is in same directory
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from agentshield_tester import AgentShieldSecurityTester
    
    # Load agent config (minimal for local tests)
    agent_config = {
        "name": "LocalTest",
        "platform": "OpenClaw",
        "audit_id": audit_id
    }
    
    # Initialize tester
    tester = AgentShieldSecurityTester(
        agent_config=agent_config,
        system_prompt="",  # Local tests don't need actual prompts
        tools_config=[]
    )
    
    # Run all 77 tests
    results = tester.run_all_tests()
    
    # Print summary
    total = results.get('total_tests', 0)
    passed = results.get('tests_passed', 0)
    score = results.get('overall_score', 0)
    print(f"✓ Tests completed: {passed}/{total} passed")
    print(f"  Security Score: {score}/100")
    
    return results


def complete_audit(audit_id: str, test_results: dict) -> dict:
    """Submit test results and receive certificate."""
    import requests
    
    # Convert new format (77 tests) to server-compatible summary format
    summary = {
        "security_score": test_results.get('security_score', 0),
        "tests_passed": test_results.get('tests_passed', 0),
        "tests_total": test_results.get('tests_total', 0),
        "tier": test_results.get('tier', 'UNKNOWN'),
        "critical_failures": test_results.get('critical_failures', 0),
        "high_failures": test_results.get('high_failures', 0),
        "medium_failures": test_results.get('medium_failures', 0)
    }
    
    payload = {
        "audit_id": audit_id,
        "test_results": summary,
        "detailed_results": test_results.get('test_results', [])  # Full details
    }
    
    response = requests.post(
        f"{AGENTSHIELD_API}/api/agent-audit/complete",
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def save_certificate(certificate: dict):
    """Save certificate to local storage."""
    ensure_directory()
    with open(CERT_FILE, 'w') as f:
        json.dump(certificate, f, indent=2)
    os.chmod(CERT_FILE, 0o644)


def main():
    parser = argparse.ArgumentParser(
        description="Initiate AgentShield security audit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect everything from files (recommended)
  python initiate_audit.py --auto
  
  # Manual specification (no file access needed)
  python initiate_audit.py --name "MyAgent" --platform telegram
  
  # Privacy-first: No environment variable scanning
  python initiate_audit.py --auto
        """
    )
    
    parser.add_argument("--name", help="Agent name/identifier")
    parser.add_argument("--platform", default="openclaw", help="Platform (telegram, discord, etc.)")
    parser.add_argument("--version", help="Agent/OpenClaw version")
    parser.add_argument("--auto", action="store_true", help="Auto-detect agent info from files only (no env scanning)")
    
    args = parser.parse_args()
    
    # Determine mode: auto or manual
    if args.auto:
        print("🔍 Auto-detecting agent information...")
        detected = auto_detect_all()
        
        print(f"\n  Detected name: {detected['name'] or 'UNKNOWN'} (confidence: {detected['name_confidence']:.0%})")
        print(f"  Detected platform: {detected['platform']} (confidence: {detected['platform_confidence']:.0%})")
        if detected['version']:
            print(f"  Detected version: {detected['version']}")
        
        # Use detected values
        agent_name = detected['name'] or "UnknownAgent"
        platform = detected['platform']
        version = detected['version']
        
        # Always confirm in auto mode (no --yes bypass for privacy)
        if detected['overall_confidence'] < 0.8:
            print(f"\n⚠️  Low confidence in auto-detection ({detected['overall_confidence']:.0%})")
            response = input(f"Use detected values? [Y/n] ").strip().lower()
            if response and response not in ('y', 'yes'):
                print("Please run with --name and --platform flags instead.")
                sys.exit(0)
        
    else:
        # Manual mode - require name
        if not args.name:
            print("Error: --name is required (or use --auto for auto-detection)")
            print("\nRun with --help for usage information.")
            sys.exit(1)
        
        agent_name = args.name
        platform = args.platform
        version = args.version
    
    print(f"\n🔐 AgentShield Security Audit")
    print(f"   Agent: {agent_name}")
    print(f"   Platform: {platform}")
    if version:
        print(f"   Version: {version}")
    print()
    
    # Step 1: Load or create keys
    keys = load_or_create_keys()
    public_key_short = keys['public_key'][:16] + "..."
    print(f"✓ Identity loaded: {public_key_short}")
    
    # Step 2: Initiate audit
    print(f"\n📡 Contacting AgentShield API...")
    try:
        session = initiate_audit(agent_name, platform, version)
    except SystemExit:
        raise
    except Exception as e:
        print(f"✗ Failed to initiate audit: {e}")
        sys.exit(1)
    
    audit_id = session.get('audit_id')
    challenge = session.get('challenge')
    
    print(f"✓ Audit initiated: {audit_id}")
    
    # Step 3: Complete challenge
    print(f"\n🔑 Authenticating...")
    try:
        auth_result = complete_challenge(audit_id, challenge, keys['private_key'])
        print(f"✓ Authentication successful")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        sys.exit(1)
    
    # Step 4: Run security tests
    print(f"\n🧪 Running security tests...")
    test_results = run_security_tests(audit_id)
    overall_score = test_results.get('security_score', 0)
    tests_passed = test_results.get('tests_passed', 0)
    tests_total = test_results.get('tests_total', 0)
    print(f"✓ Tests completed: {tests_passed}/{tests_total} passed")
    print(f"   Security Score: {overall_score}/100")
    
    # Step 5: Complete and get certificate
    print(f"\n📜 Requesting certificate...")
    try:
        result = complete_audit(audit_id, test_results)
        certificate = result.get('certificate')
        agent_id = result.get('agent_id')
        
        if certificate:
            save_certificate(certificate)
            payload = certificate.get('payload', {})
            tier = payload.get('tier', result.get('tier', 'UNKNOWN'))
            score = payload.get('score', result.get('security_score', 0))
            expires = result.get('expires_at')
            
            print(f"\n{'='*50}")
            print(f"✅ AUDIT COMPLETE")
            print(f"{'='*50}")
            print(f"Security Score: {score}/100")
            print(f"Tier: {tier}")
            print(f"Valid until: {expires}")
            print(f"Agent ID: {agent_id}")
            print(f"{'='*50}")
            print(f"\nCertificate saved to: {CERT_FILE}")
            print(f"Other agents can verify you at: {AGENTSHIELD_API}/api/verify/{agent_id}")
        else:
            print("✗ No certificate received")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Failed to complete audit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
