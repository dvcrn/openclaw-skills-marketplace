# Required Credentials & Configuration

This skill requires external API credentials and configuration for full functionality.

## Required API Credentials

### eBay API (Core Functionality)
```bash
export EBAY_APP_ID="your_production_app_id"
export EBAY_CERT_ID="your_production_cert_id"  
export EBAY_DEV_ID="your_production_dev_id"
export EBAY_USER_TOKEN="your_production_user_token"
```
**Purpose**: Market data retrieval, listing creation, sold listings analysis
**Permissions**: Read marketplace data, manage user listings
**Registration**: https://developer.ebay.com/

### PSA API (Population Data)
```bash
export PSA_API_KEY="your_psa_api_key"
```
**Purpose**: Card population data, certification verification
**Permissions**: Read population reports, verify certifications
**Registration**: Contact PSA for API access

### Social Media APIs (Market Sentiment)

**Twitter API v2**
```bash
export TWITTER_BEARER_TOKEN="your_twitter_bearer_token"
export TWITTER_API_KEY="your_twitter_api_key"
export TWITTER_API_SECRET="your_twitter_api_secret"
```
**Purpose**: Market sentiment analysis, trending topics
**Permissions**: Read tweets, search tweets
**Registration**: https://developer.twitter.com/

**Reddit API**
```bash
export REDDIT_CLIENT_ID="your_reddit_client_id"
export REDDIT_CLIENT_SECRET="your_reddit_client_secret"
```
**Purpose**: Community discussions, market sentiment
**Permissions**: Read posts and comments
**Registration**: https://www.reddit.com/prefs/apps

## Optional Integrations

### Sports Data APIs
```bash
export SPORTS_REFERENCE_API_KEY="your_sports_api_key"
```
**Purpose**: Player statistics correlation with card values
**Permissions**: Read player and team statistics
**Registration**: https://www.sports-reference.com/

### Discord Notifications
```bash
export DISCORD_WEBHOOK_URL="your_discord_webhook"
```
**Purpose**: Market alerts and daily briefings
**Setup**: Create webhook in Discord server settings

### Email Notifications
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_USERNAME="your_email@gmail.com"
export SMTP_PASSWORD="your_app_password"
```
**Purpose**: Detailed reports and alerts via email

## Database Configuration

### PostgreSQL (Recommended)
```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/trading_cards"
```
**Purpose**: Market data storage, portfolio tracking, intelligence cache

### MongoDB (Optional - for unstructured data)
```bash
export MONGODB_URI="mongodb://localhost:27017/trading_cards"
```
**Purpose**: Social media data, market trends, competitor intelligence

## Security Configuration

### Encryption
```bash
export ENCRYPTION_PASSWORD="your_secure_encryption_password"
export ENCRYPTION_SALT="your_unique_salt_value"
```
**Purpose**: Encrypt sensitive portfolio and card data

## Functionality by Credential Tier

### Tier 1: Basic (No credentials required)
- Card image analysis (limited accuracy)
- Basic market research
- Manual listing optimization
- Educational content access

### Tier 2: eBay Integration
**Required**: EBAY_* credentials
- Real-time market pricing
- Sold listings analysis
- Automated listing creation
- Competition monitoring

### Tier 3: Full Intelligence
**Required**: eBay + PSA + Social Media credentials
- Population data analysis
- Market sentiment tracking
- Advanced competitor intelligence
- Predictive analytics

### Tier 4: Premium Automation
**Required**: All API credentials + Database
- Automated portfolio management
- Real-time market monitoring
- Custom intelligence reports
- Multi-platform optimization

## Setup Instructions

### 1. Create Credential Files
```bash
# Create secure credential storage
touch ~/.trading_card_credentials
chmod 600 ~/.trading_card_credentials

# Add to your shell profile (.bashrc, .zshrc, etc.)
source ~/.trading_card_credentials
```

### 2. Obtain API Credentials
1. **eBay Developer Account**: Register at developer.ebay.com
2. **PSA API Access**: Contact PSA for business API access
3. **Social Media APIs**: Register developer accounts
4. **Database Setup**: Install and configure PostgreSQL

### 3. Test Configuration
```bash
# Test script to validate credentials
python3 scripts/test_credentials.py
```

### 4. Security Validation
```bash
# Verify secure credential storage
python3 scripts/security_check.py
```

## Privacy & Compliance Notes

- **Data Storage**: All credentials stored locally, never transmitted to third parties
- **API Usage**: Complies with each platform's terms of service and rate limits
- **Audit Logging**: All API calls logged for compliance and debugging
- **User Consent**: Required before accessing external platforms

## Troubleshooting

### Common Issues
1. **"Invalid eBay Token"**: Check token expiration, refresh as needed
2. **"PSA API Unavailable"**: Verify API key and check PSA system status
3. **"Rate Limited"**: Respect platform rate limits, implement backoff
4. **"Permission Denied"**: Ensure API credentials have necessary permissions

### Support Resources
- eBay Developer Forums
- PSA Support (for API access)
- Platform-specific documentation in references/ folder