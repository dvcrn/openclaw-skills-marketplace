# Security & Compliance Guide

## Core Security Principles

### API Token Management
```bash
# Environment Variables (REQUIRED)
export EBAY_APP_ID="your_ebay_app_id"
export EBAY_CERT_ID="your_ebay_cert_id" 
export EBAY_DEV_ID="your_ebay_dev_id"
export EBAY_USER_TOKEN="your_ebay_user_token"
export PSA_API_KEY="your_psa_api_key"
export TWITTER_BEARER_TOKEN="your_twitter_bearer_token"
export REDDIT_CLIENT_ID="your_reddit_client_id"
export REDDIT_CLIENT_SECRET="your_reddit_client_secret"

# NEVER hardcode tokens in scripts or config files
# ❌ WRONG: api_key = "abc123def456"  
# ✅ CORRECT: api_key = os.getenv('PSA_API_KEY')
```

### Token Security Best Practices
```python
import os
import keyring
from cryptography.fernet import Fernet

def secure_token_management():
    """Best practices for API token security"""
    
    # 1. Environment variables for development
    api_key = os.getenv('PSA_API_KEY')
    if not api_key:
        raise ValueError("PSA_API_KEY environment variable not set")
    
    # 2. System keyring for production (recommended)
    def store_token_securely(service, username, token):
        keyring.set_password(service, username, token)
    
    def retrieve_token_securely(service, username):
        return keyring.get_password(service, username)
    
    # 3. Encrypted storage for sensitive environments
    def encrypt_token(token, key):
        f = Fernet(key)
        encrypted_token = f.encrypt(token.encode())
        return encrypted_token
    
    return {
        'environment_based': api_key,
        'keyring_storage': retrieve_token_securely,
        'encrypted_storage': encrypt_token
    }
```

### Token Rotation Schedule
```python
def implement_token_rotation():
    """Automated token rotation for security"""
    
    rotation_schedule = {
        'ebay_tokens': {
            'frequency': 'every_18_months',  # eBay requirement
            'renewal_process': 'oauth_refresh',
            'monitoring': 'expiration_alerts'
        },
        'psa_api_key': {
            'frequency': 'quarterly',
            'renewal_process': 'manual_regeneration',
            'monitoring': 'usage_tracking'
        },
        'social_media_tokens': {
            'frequency': 'monthly',
            'renewal_process': 'automated_refresh',
            'monitoring': 'rate_limit_tracking'
        }
    }
    
    # Automated renewal alerts
    def schedule_renewal_alerts():
        import schedule
        import time
        
        def check_token_expiration():
            for service, config in rotation_schedule.items():
                days_until_expiry = get_days_until_expiry(service)
                if days_until_expiry <= 30:
                    send_renewal_alert(service, days_until_expiry)
        
        schedule.every().day.do(check_token_expiration)
    
    return rotation_schedule
```

## Web Scraping Ethics & Compliance

### robots.txt Compliance
```python
import urllib.robotparser
import time
import random

def ethical_scraping_framework():
    """Comprehensive ethical scraping implementation"""
    
    class EthicalScraper:
        def __init__(self, base_url, user_agent):
            self.base_url = base_url
            self.user_agent = user_agent
            self.robots_parser = self.load_robots_txt()
            self.rate_limiter = self.setup_rate_limiting()
        
        def load_robots_txt(self):
            """Check and respect robots.txt"""
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{self.base_url}/robots.txt")
            try:
                rp.read()
                return rp
            except Exception:
                # If robots.txt unavailable, err on side of caution
                return None
        
        def can_fetch(self, url):
            """Check if URL can be fetched per robots.txt"""
            if self.robots_parser:
                return self.robots_parser.can_fetch(self.user_agent, url)
            # If no robots.txt, allow but with extra caution
            return True
        
        def setup_rate_limiting(self):
            """Implement respectful rate limiting"""
            def rate_limited_request(url, min_delay=2, max_delay=5):
                if not self.can_fetch(url):
                    raise PermissionError(f"robots.txt disallows access to {url}")
                
                # Random delay between requests (2-5 seconds)
                delay = random.uniform(min_delay, max_delay)
                time.sleep(delay)
                
                # Add respectful headers
                headers = {
                    'User-Agent': f'{self.user_agent} (Educational/Research)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                return headers
            
            return rate_limited_request
    
    return EthicalScraper
```

### Terms of Service Compliance
```python
def tos_compliance_monitoring():
    """Monitor and ensure ToS compliance across platforms"""
    
    platform_policies = {
        'ebay': {
            'last_updated': '2026-01-15',
            'key_restrictions': [
                'no_automated_bidding',
                'rate_limit_5000_per_day',
                'no_bulk_downloading',
                'commercial_use_requires_agreement'
            ],
            'review_frequency': 'quarterly',
            'contact_for_permission': 'developer-relations@ebay.com'
        },
        'psa': {
            'last_updated': '2025-12-01', 
            'key_restrictions': [
                'api_key_required',
                'rate_limit_1000_per_hour',
                'no_redistribution',
                'attribution_required'
            ],
            'review_frequency': 'quarterly',
            'contact_for_permission': 'api-support@psacard.com'
        },
        'reddit': {
            'last_updated': '2026-02-01',
            'key_restrictions': [
                'oauth_required',
                'rate_limit_60_per_minute',
                'no_vote_manipulation',
                'respect_subreddit_rules'
            ],
            'review_frequency': 'monthly',
            'contact_for_permission': 'api@reddit.com'
        }
    }
    
    def check_policy_updates():
        """Automated policy update checking"""
        for platform, policy_info in platform_policies.items():
            last_check = policy_info['last_updated']
            # Implement automated checking logic
            current_policy = fetch_current_policy(platform)
            if policy_changed(current_policy, last_check):
                send_policy_update_alert(platform, current_policy)
    
    return platform_policies
```

### User Consent Framework
```python
def user_consent_management():
    """Comprehensive user consent for automated activities"""
    
    consent_framework = {
        'data_collection': {
            'required_disclosures': [
                'what_data_collected',
                'how_data_used', 
                'data_retention_period',
                'third_party_sharing',
                'user_rights'
            ],
            'consent_mechanisms': [
                'explicit_opt_in',
                'granular_permissions',
                'withdrawal_process',
                'consent_logging'
            ]
        },
        'automated_actions': {
            'user_authorization': [
                'scraping_consent',
                'api_access_consent',
                'social_monitoring_consent',
                'competitive_analysis_consent'
            ],
            'transparency_requirements': [
                'activity_logging',
                'user_dashboards',
                'audit_trails',
                'data_export'
            ]
        }
    }
    
    def get_user_consent(activity_type, data_sources):
        """Get explicit user consent for automated activities"""
        consent_text = generate_consent_text(activity_type, data_sources)
        user_response = request_user_consent(consent_text)
        log_consent_decision(activity_type, user_response)
        return user_response
    
    def validate_ongoing_consent():
        """Regularly validate that consent is still valid"""
        for activity in active_automated_activities():
            if consent_expired(activity) or consent_withdrawn(activity):
                stop_automated_activity(activity)
                request_renewed_consent(activity)
    
    return consent_framework
```

## Data Protection & Privacy

### Data Encryption Standards
```python
def implement_data_encryption():
    """Comprehensive data encryption implementation"""
    
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import os
    import base64
    
    class DataEncryption:
        def __init__(self, password=None):
            self.password = password or os.getenv('ENCRYPTION_PASSWORD')
            self.key = self.derive_key(self.password)
            self.cipher = Fernet(self.key)
        
        def derive_key(self, password):
            """Derive encryption key from password"""
            salt = os.getenv('ENCRYPTION_SALT', 'default_salt').encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key
        
        def encrypt_sensitive_data(self, data):
            """Encrypt sensitive card and portfolio data"""
            if isinstance(data, str):
                data = data.encode()
            encrypted_data = self.cipher.encrypt(data)
            return base64.urlsafe_b64encode(encrypted_data)
        
        def decrypt_sensitive_data(self, encrypted_data):
            """Decrypt sensitive data for processing"""
            decoded_data = base64.urlsafe_b64decode(encrypted_data)
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        
        def encrypt_database_backup(self, backup_file):
            """Encrypt database backups"""
            with open(backup_file, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self.cipher.encrypt(file_data)
            
            with open(f"{backup_file}.encrypted", 'wb') as f:
                f.write(encrypted_data)
            
            # Securely delete original
            os.remove(backup_file)
    
    return DataEncryption()
```

### Privacy Compliance (GDPR/CCPA)
```python
def privacy_compliance_framework():
    """GDPR and CCPA compliance implementation"""
    
    compliance_requirements = {
        'gdpr': {
            'data_subject_rights': [
                'right_to_access',
                'right_to_rectification', 
                'right_to_erasure',
                'right_to_restrict_processing',
                'right_to_data_portability',
                'right_to_object'
            ],
            'legal_basis': [
                'consent',
                'legitimate_interest',
                'contract_performance'
            ],
            'breach_notification': '72_hours_to_authority'
        },
        'ccpa': {
            'consumer_rights': [
                'right_to_know',
                'right_to_delete',
                'right_to_opt_out',
                'right_to_non_discrimination'
            ],
            'disclosure_requirements': [
                'categories_of_personal_info',
                'purposes_for_collection',
                'sources_of_information',
                'third_party_sharing'
            ]
        }
    }
    
    def handle_data_subject_request(request_type, user_id):
        """Handle GDPR/CCPA data subject requests"""
        if request_type == 'access':
            return export_user_data(user_id)
        elif request_type == 'deletion':
            return delete_user_data(user_id)
        elif request_type == 'rectification':
            return update_user_data(user_id)
        elif request_type == 'portability':
            return export_portable_data(user_id)
    
    def log_data_processing_activity():
        """Maintain GDPR-compliant processing records"""
        processing_record = {
            'controller_details': get_controller_details(),
            'purposes_of_processing': get_processing_purposes(),
            'categories_of_data_subjects': get_data_subject_categories(),
            'categories_of_personal_data': get_personal_data_categories(),
            'retention_periods': get_retention_periods(),
            'security_measures': get_security_measures()
        }
        return processing_record
    
    return compliance_requirements
```

## Network Security

### Tailscale Configuration
```bash
# Recommended Tailscale ACL for trading card database access
{
  "acls": [
    {
      "action": "accept",
      "src": ["your-agent@yourdomain.com"],
      "dst": ["card-database:22", "card-database:3306", "card-database:5432"]
    },
    {
      "action": "accept", 
      "src": ["trading-card-agents"],
      "dst": ["api-servers:443", "backup-servers:22"]
    }
  ],
  "groups": {
    "trading-card-agents": [
      "your-agent@yourdomain.com",
      "backup-agent@yourdomain.com"
    ]
  },
  "tagOwners": {
    "tag:card-database": ["your-agent@yourdomain.com"],
    "tag:api-server": ["admin@yourdomain.com"]
  }
}
```

### Database Security Configuration
```sql
-- PostgreSQL security configuration for trading card data

-- Create dedicated database user for trading card operations
CREATE USER trading_card_agent WITH PASSWORD 'secure_random_password';

-- Grant minimal necessary privileges
GRANT CONNECT ON DATABASE trading_cards TO trading_card_agent;
GRANT USAGE ON SCHEMA public TO trading_card_agent;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO trading_card_agent;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO trading_card_agent;

-- Enable row-level security
ALTER TABLE portfolio_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY user_portfolio_access ON portfolio_holdings
    FOR ALL TO trading_card_agent
    USING (user_id = current_setting('app.current_user_id')::INTEGER);

-- Enable SSL connections only
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/server.crt';
ALTER SYSTEM SET ssl_key_file = '/path/to/server.key';

-- Configure connection security
ALTER SYSTEM SET listen_addresses = 'localhost,tailscale-ip';
ALTER SYSTEM SET port = 5432;
```

## Audit Logging & Monitoring

### Comprehensive Audit Logging
```python
def setup_audit_logging():
    """Comprehensive audit logging for all system activities"""
    
    import logging
    import json
    from datetime import datetime
    
    class AuditLogger:
        def __init__(self, log_file='trading_card_audit.log'):
            self.logger = logging.getLogger('trading_card_audit')
            self.logger.setLevel(logging.INFO)
            
            # File handler for persistent logging
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        def log_api_call(self, api_name, endpoint, user_id, response_code):
            """Log all API calls for audit trail"""
            audit_entry = {
                'event_type': 'api_call',
                'api_name': api_name,
                'endpoint': endpoint,
                'user_id': user_id,
                'response_code': response_code,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': self.get_client_ip()
            }
            self.logger.info(json.dumps(audit_entry))
        
        def log_data_access(self, user_id, table_name, action, record_count):
            """Log database access for compliance"""
            audit_entry = {
                'event_type': 'data_access',
                'user_id': user_id,
                'table_name': table_name,
                'action': action,  # SELECT, INSERT, UPDATE, DELETE
                'record_count': record_count,
                'timestamp': datetime.utcnow().isoformat()
            }
            self.logger.info(json.dumps(audit_entry))
        
        def log_security_event(self, event_type, description, severity='medium'):
            """Log security-related events"""
            audit_entry = {
                'event_type': 'security_event',
                'security_event_type': event_type,
                'description': description,
                'severity': severity,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': self.get_client_ip()
            }
            self.logger.warning(json.dumps(audit_entry))
    
    return AuditLogger()
```

### Security Monitoring Alerts
```python
def setup_security_monitoring():
    """Real-time security monitoring and alerting"""
    
    security_thresholds = {
        'failed_api_calls': {
            'threshold': 10,
            'timeframe': '5_minutes',
            'action': 'temporary_ip_block'
        },
        'unusual_data_access': {
            'threshold': 100,
            'timeframe': '1_hour',
            'action': 'admin_alert'
        },
        'token_usage_spike': {
            'threshold': 500,
            'timeframe': '1_hour', 
            'action': 'rate_limit_enforcement'
        }
    }
    
    def monitor_security_metrics():
        """Monitor security metrics in real-time"""
        current_metrics = gather_security_metrics()
        
        for metric_name, threshold_config in security_thresholds.items():
            current_value = current_metrics.get(metric_name, 0)
            
            if current_value > threshold_config['threshold']:
                trigger_security_response(metric_name, current_value, threshold_config)
    
    def trigger_security_response(metric_name, value, config):
        """Automated security response to threats"""
        alert_message = f"Security threshold exceeded: {metric_name} = {value}"
        
        if config['action'] == 'temporary_ip_block':
            implement_temporary_ip_block()
        elif config['action'] == 'admin_alert':
            send_admin_security_alert(alert_message)
        elif config['action'] == 'rate_limit_enforcement':
            enforce_strict_rate_limits()
    
    return security_thresholds
```

## Production Security Checklist

### Deployment Security Validation
```python
def production_security_checklist():
    """Pre-deployment security validation checklist"""
    
    security_checks = {
        'authentication': {
            'api_keys_in_environment': check_api_keys_not_hardcoded(),
            'token_rotation_scheduled': check_token_rotation_setup(),
            'multi_factor_auth': check_mfa_enabled(),
            'secure_key_storage': check_keyring_usage()
        },
        'data_protection': {
            'encryption_at_rest': check_database_encryption(),
            'encryption_in_transit': check_ssl_certificates(),
            'backup_encryption': check_backup_security(),
            'data_retention_policy': check_retention_compliance()
        },
        'network_security': {
            'tailscale_acl_configured': check_tailscale_config(),
            'firewall_rules': check_firewall_configuration(),
            'intrusion_detection': check_ids_setup(),
            'vpn_access_only': check_vpn_requirements()
        },
        'compliance': {
            'gdpr_compliance': check_gdpr_implementation(),
            'audit_logging': check_audit_log_setup(),
            'incident_response_plan': check_incident_procedures(),
            'privacy_policy_updated': check_privacy_documentation()
        }
    }
    
    def validate_security_posture():
        """Run complete security validation"""
        failed_checks = []
        
        for category, checks in security_checks.items():
            for check_name, check_function in checks.items():
                try:
                    result = check_function()
                    if not result:
                        failed_checks.append(f"{category}.{check_name}")
                except Exception as e:
                    failed_checks.append(f"{category}.{check_name}: {str(e)}")
        
        if failed_checks:
            raise SecurityValidationError(
                f"Security validation failed: {failed_checks}"
            )
        
        return True
    
    return validate_security_posture
```

### Emergency Response Procedures
```python
def emergency_security_procedures():
    """Emergency response procedures for security incidents"""
    
    incident_response_plan = {
        'detection': {
            'automated_monitoring': 'real_time_alerts',
            'manual_reporting': 'incident_report_form',
            'third_party_notification': 'external_security_alerts'
        },
        'containment': {
            'immediate_actions': [
                'revoke_compromised_tokens',
                'block_suspicious_ip_addresses',
                'disable_affected_user_accounts',
                'isolate_compromised_systems'
            ],
            'communication': [
                'notify_incident_response_team',
                'prepare_stakeholder_communication',
                'document_initial_assessment'
            ]
        },
        'investigation': {
            'evidence_collection': [
                'preserve_system_logs',
                'capture_network_traffic',
                'document_attack_vectors',
                'interview_affected_users'
            ],
            'analysis': [
                'determine_scope_of_breach',
                'identify_compromised_data',
                'assess_business_impact',
                'develop_remediation_plan'
            ]
        },
        'recovery': {
            'system_restoration': [
                'patch_security_vulnerabilities',
                'restore_from_clean_backups',
                'implement_additional_controls',
                'validate_system_integrity'
            ],
            'business_continuity': [
                'resume_critical_operations',
                'communicate_with_customers',
                'monitor_for_recurring_issues',
                'update_security_procedures'
            ]
        }
    }
    
    return incident_response_plan
```