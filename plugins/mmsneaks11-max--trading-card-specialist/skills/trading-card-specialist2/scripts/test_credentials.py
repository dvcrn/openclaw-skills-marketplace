#!/usr/bin/env python3
"""
Credential Validation Script
Tests that required API credentials are properly configured
"""

import os
import sys
from typing import Dict, List

def check_credentials() -> Dict[str, bool]:
    """Check if required credentials are configured"""
    
    required_credentials = {
        'eBay API': [
            'EBAY_APP_ID',
            'EBAY_CERT_ID', 
            'EBAY_DEV_ID',
            'EBAY_USER_TOKEN'
        ],
        'PSA API': [
            'PSA_API_KEY'
        ],
        'Twitter API': [
            'TWITTER_BEARER_TOKEN',
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET'
        ],
        'Reddit API': [
            'REDDIT_CLIENT_ID',
            'REDDIT_CLIENT_SECRET'
        ],
        'Database': [
            'DATABASE_URL'
        ],
        'Security': [
            'ENCRYPTION_PASSWORD'
        ]
    }
    
    optional_credentials = {
        'Discord Notifications': ['DISCORD_WEBHOOK_URL'],
        'Email Notifications': ['SMTP_SERVER', 'SMTP_USERNAME', 'SMTP_PASSWORD'],
        'Sports Data': ['SPORTS_REFERENCE_API_KEY'],
        'MongoDB': ['MONGODB_URI']
    }
    
    results = {}
    
    print("🔍 Checking Required Credentials")
    print("=" * 40)
    
    for service, env_vars in required_credentials.items():
        all_present = all(os.getenv(var) for var in env_vars)
        results[service] = all_present
        
        status = "✅ CONFIGURED" if all_present else "❌ MISSING"
        print(f"{service:20} {status}")
        
        if not all_present:
            missing = [var for var in env_vars if not os.getenv(var)]
            print(f"                     Missing: {', '.join(missing)}")
    
    print("\n🔧 Checking Optional Credentials") 
    print("=" * 40)
    
    for service, env_vars in optional_credentials.items():
        all_present = all(os.getenv(var) for var in env_vars)
        
        status = "✅ CONFIGURED" if all_present else "⚪ OPTIONAL"
        print(f"{service:20} {status}")
    
    return results

def validate_credential_format() -> bool:
    """Basic format validation for credentials"""
    
    print("\n🧪 Validating Credential Formats")
    print("=" * 40)
    
    validation_errors = []
    
    # Check eBay credentials format
    ebay_app_id = os.getenv('EBAY_APP_ID')
    if ebay_app_id and not ebay_app_id.startswith(('YourDev-', 'YourProd-')):
        validation_errors.append("eBay App ID format appears invalid")
    
    # Check PSA API key
    psa_key = os.getenv('PSA_API_KEY')
    if psa_key and len(psa_key) < 20:
        validation_errors.append("PSA API key appears too short")
    
    # Check Twitter bearer token
    twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
    if twitter_token and not twitter_token.startswith('AAAA'):
        validation_errors.append("Twitter Bearer Token format appears invalid")
    
    # Check database URL
    db_url = os.getenv('DATABASE_URL')
    if db_url and not db_url.startswith(('postgresql://', 'postgres://')):
        validation_errors.append("Database URL should be PostgreSQL format")
    
    if validation_errors:
        for error in validation_errors:
            print(f"⚠️  {error}")
        return False
    else:
        print("✅ All configured credentials appear valid")
        return True

def check_network_access() -> bool:
    """Test basic network connectivity to required services"""
    
    print("\n🌐 Checking Network Access")
    print("=" * 40)
    
    import socket
    
    services = {
        'eBay API': ('api.ebay.com', 443),
        'PSA API': ('api.psacard.com', 443), 
        'Twitter API': ('api.twitter.com', 443),
        'Reddit API': ('www.reddit.com', 443)
    }
    
    all_accessible = True
    
    for service_name, (host, port) in services.items():
        try:
            socket.create_connection((host, port), timeout=5)
            print(f"{service_name:20} ✅ ACCESSIBLE")
        except socket.error:
            print(f"{service_name:20} ❌ UNREACHABLE")
            all_accessible = False
    
    return all_accessible

def generate_setup_report(results: Dict[str, bool]) -> None:
    """Generate a setup recommendation report"""
    
    print("\n📊 Setup Recommendations")
    print("=" * 40)
    
    essential_services = ['eBay API']
    recommended_services = ['PSA API', 'Twitter API', 'Reddit API'] 
    
    # Check essential services
    missing_essential = [service for service in essential_services if not results.get(service)]
    if missing_essential:
        print(f"🚨 CRITICAL: Missing essential services: {', '.join(missing_essential)}")
        print("   Basic functionality will be severely limited without these.")
    
    # Check recommended services
    missing_recommended = [service for service in recommended_services if not results.get(service)]
    if missing_recommended:
        print(f"⚠️  RECOMMENDED: Consider adding: {', '.join(missing_recommended)}")
        print("   These enable advanced market intelligence features.")
    
    # Calculate functionality percentage
    total_services = len(results)
    configured_services = sum(results.values())
    functionality_pct = (configured_services / total_services) * 100
    
    print(f"\n📈 Estimated Functionality: {functionality_pct:.0f}%")
    
    if functionality_pct >= 80:
        print("✅ Excellent setup! Most features will be available.")
    elif functionality_pct >= 60:
        print("✅ Good setup! Core features will work well.")
    elif functionality_pct >= 40:
        print("⚠️  Basic setup. Many advanced features will be limited.")
    else:
        print("🚨 Minimal setup. Consider adding more credentials for full functionality.")

def main():
    print("Trading Card Specialist - Credential Validation")
    print("=" * 50)
    
    # Check credentials
    results = check_credentials()
    
    # Validate formats
    format_valid = validate_credential_format()
    
    # Check network access
    network_ok = check_network_access()
    
    # Generate recommendations
    generate_setup_report(results)
    
    # Overall status
    essential_configured = results.get('eBay API', False)
    
    if essential_configured and format_valid and network_ok:
        print(f"\n✅ READY TO USE")
        print("The skill is properly configured and ready for use.")
        sys.exit(0)
    elif essential_configured:
        print(f"\n⚠️  READY WITH LIMITATIONS")  
        print("Basic functionality available. See recommendations above.")
        sys.exit(0)
    else:
        print(f"\n❌ NOT READY")
        print("Essential credentials missing. See CREDENTIALS.md for setup instructions.")
        sys.exit(1)

if __name__ == '__main__':
    main()