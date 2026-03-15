# Security Guidelines

## Overview

The G-Prophet API skill connects to an external service (https://www.gprophet.com) to provide AI-powered stock predictions and market analysis. This document outlines security best practices for using this skill.

## API Key Management

### Obtaining API Keys

1. Visit https://www.gprophet.com/settings/api-keys
2. Create a new API key with appropriate permissions
3. API keys follow the format: `gp_sk_*`

### Secure Storage

**Recommended Method**: Environment Variables

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export GPROPHET_API_KEY="gp_sk_your_key_here"
```

**Alternative Methods**:
- Use your platform's secure credential store
- Use a secrets management service (e.g., HashiCorp Vault, AWS Secrets Manager)

**Never**:
- ❌ Commit API keys to version control
- ❌ Store keys in plain text files in your repository
- ❌ Share keys in chat logs, screenshots, or public forums
- ❌ Use production keys for testing or development

### Key Rotation

- Rotate API keys every 90 days
- Immediately revoke keys if:
  - They may have been exposed
  - An employee with access leaves
  - You suspect unauthorized usage

## Data Privacy

### What Data is Sent

This skill sends the following data to the G-Prophet API:
- Stock symbols (e.g., AAPL, 600519)
- Market codes (US, CN, HK, CRYPTO)
- Prediction parameters (days, algorithms)
- Your API key (for authentication)

### What Data is NOT Sent

- Personal information
- Trading credentials or brokerage account details
- Portfolio holdings or positions
- Financial account information

## Network Security

### API Endpoint

All requests are sent to: `https://www.gprophet.com/api/external/v1`

- Uses HTTPS/TLS encryption
- Verify the certificate is valid
- Do not disable SSL verification

### Firewall Configuration

If your network requires allowlisting:
- Domain: `www.gprophet.com`
- Port: 443 (HTTPS)

## Monitoring & Auditing

### Usage Monitoring

Monitor your API usage at: https://www.gprophet.com/dashboard

Watch for:
- Unexpected spikes in usage
- Calls from unknown IP addresses
- Unusual patterns or timing

### Billing Alerts

Set up billing alerts to detect:
- Excessive point consumption
- Potential API key abuse
- Budget overruns

## Incident Response

If you suspect your API key has been compromised:

1. **Immediately revoke the key** at https://www.gprophet.com/settings/api-keys
2. **Generate a new key** with a different name
3. **Review usage logs** for unauthorized activity
4. **Update your environment** with the new key
5. **Report the incident** to support@gprophet.com

## Compliance

### Financial Data

This skill provides predictions and analysis for informational purposes only. It does not:
- Execute trades
- Access brokerage accounts
- Store financial transactions
- Provide regulated financial advice

### Data Retention

- API requests are logged by G-Prophet for service operation
- Logs are retained according to G-Prophet's privacy policy
- No local data is stored by this skill

## Testing & Evaluation

### Before Production Use

1. Create a test API key with limited permissions
2. Set a low point balance for testing
3. Test with non-sensitive symbols
4. Monitor usage during evaluation period
5. Verify billing behavior matches expectations

### Recommended Test Approach

```bash
# Use a separate test key
export GPROPHET_API_KEY="gp_sk_test_your_test_key"

# Test with common symbols
/gprophet predict AAPL US 7

# Monitor points consumed
# Check dashboard: https://www.gprophet.com/dashboard
```

## Support & Reporting

### Security Issues

Report security vulnerabilities to:
- Email: security@gprophet.com
- Do not disclose publicly until patched

### General Support

- Documentation: https://www.gprophet.com/docs
- Support: support@gprophet.com
- Status: https://www.gprophet.com/status

## Additional Resources

- Privacy Policy: https://www.gprophet.com/privacy
- Terms of Service: https://www.gprophet.com/terms
- API Documentation: https://www.gprophet.com/docs/api

---

Last Updated: 2026-03-04
