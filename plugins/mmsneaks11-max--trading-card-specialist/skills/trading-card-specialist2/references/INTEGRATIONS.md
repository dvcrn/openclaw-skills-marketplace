# Integration Setup & Configuration Guide

## Platform API Integrations

### eBay API Integration
```python
def setup_ebay_integration(credentials, environment='production'):
    """
    Complete eBay API integration setup for trading card operations
    """
    ebay_config = {
        'trading_api': {
            'endpoint': 'https://api.ebay.com/ws/api.dll',
            'app_id': credentials['app_id'],
            'dev_id': credentials['dev_id'],
            'cert_id': credentials['cert_id'],
            'user_token': credentials['user_token'],
            'capabilities': [
                'GetItem',
                'GetSellerList',
                'AddFixedPriceItem', 
                'ReviseFixedPriceItem',
                'EndFixedPriceItem',
                'GetCategories',
                'GetItemTransactions'
            ]
        },
        'browse_api': {
            'endpoint': 'https://api.ebay.com/buy/browse/v1',
            'access_token': credentials['oauth_token'],
            'capabilities': [
                'search',
                'get_item_summary',
                'get_item',
                'get_item_by_legacy_id'
            ]
        },
        'sell_api': {
            'endpoint': 'https://api.ebay.com/sell',
            'access_token': credentials['oauth_token'],
            'capabilities': [
                'inventory_management',
                'offer_management',
                'listing_optimization',
                'analytics_reporting'
            ]
        }
    }
    
    # Rate limiting configuration
    rate_limits = {
        'trading_api': '5000_calls_per_day',
        'browse_api': 'unlimited',
        'sell_api': '10000_calls_per_day'
    }
    
    return configure_ebay_client(ebay_config, rate_limits)
```

### PSA API Integration
```python
def setup_psa_integration(api_key, certification_config):
    """
    PSA API integration for population and certification data
    """
    psa_endpoints = {
        'population_lookup': {
            'url': 'https://api.psacard.com/v1/population',
            'authentication': f'Bearer {api_key}',
            'methods': ['GET'],
            'parameters': [
                'card_id',
                'year',
                'sport', 
                'manufacturer',
                'card_number'
            ]
        },
        'cert_verification': {
            'url': 'https://api.psacard.com/v1/cert',
            'authentication': f'Bearer {api_key}',
            'methods': ['GET'],
            'parameters': [
                'cert_number',
                'verification_code'
            ]
        },
        'submission_tracking': {
            'url': 'https://api.psacard.com/v1/submissions',
            'authentication': f'Bearer {api_key}',
            'methods': ['GET', 'POST'],
            'parameters': [
                'submission_id',
                'tracking_number',
                'status_updates'
            ]
        }
    }
    
    return initialize_psa_client(psa_endpoints, certification_config)
```

### Sports Reference API Integration
```python
def setup_sports_reference_integration(api_credentials):
    """
    Sports Reference API for player statistics and performance data
    """
    sports_apis = {
        'basketball': {
            'endpoint': 'https://api.sportsreference.com/basketball',
            'data_sources': [
                'player_stats',
                'team_performance',
                'playoff_results',
                'award_winners',
                'hall_of_fame'
            ]
        },
        'football': {
            'endpoint': 'https://api.sportsreference.com/football', 
            'data_sources': [
                'player_stats',
                'team_performance',
                'playoff_results',
                'award_winners',
                'draft_data'
            ]
        },
        'baseball': {
            'endpoint': 'https://api.sportsreference.com/baseball',
            'data_sources': [
                'player_stats',
                'team_performance',
                'playoff_results', 
                'award_winners',
                'hall_of_fame'
            ]
        }
    }
    
    return configure_sports_reference_client(sports_apis, api_credentials)
```

## Social Media Monitoring Setup

### Twitter API Integration
```python
def setup_twitter_monitoring(twitter_credentials, monitoring_config):
    """
    Twitter API v2 integration for market sentiment and trend monitoring
    """
    twitter_config = {
        'api_endpoints': {
            'tweets_search': 'https://api.twitter.com/2/tweets/search/recent',
            'users_lookup': 'https://api.twitter.com/2/users',
            'streaming': 'https://api.twitter.com/2/tweets/search/stream'
        },
        'authentication': {
            'bearer_token': twitter_credentials['bearer_token'],
            'api_key': twitter_credentials['api_key'],
            'api_secret': twitter_credentials['api_secret'],
            'access_token': twitter_credentials['access_token'],
            'access_token_secret': twitter_credentials['access_token_secret']
        },
        'monitoring_targets': {
            'hashtags': [
                '#tradingcards',
                '#sportscards',
                '#pokemon',
                '#baseballcards',
                '#basketballcards',
                '#footballcards'
            ],
            'keywords': monitoring_config['keywords'],
            'influencers': monitoring_config['influencer_accounts'],
            'competitors': monitoring_config['competitor_accounts']
        }
    }
    
    sentiment_analysis = setup_sentiment_analysis_pipeline(twitter_config)
    
    return initialize_twitter_monitoring(twitter_config, sentiment_analysis)
```

### Reddit API Integration
```python
def setup_reddit_monitoring(reddit_credentials, subreddit_config):
    """
    Reddit API integration for community sentiment and discussion monitoring
    """
    reddit_config = {
        'api_client': {
            'client_id': reddit_credentials['client_id'],
            'client_secret': reddit_credentials['client_secret'],
            'user_agent': reddit_credentials['user_agent'],
            'username': reddit_credentials['username'],
            'password': reddit_credentials['password']
        },
        'monitored_subreddits': [
            'r/basketballcards',
            'r/baseballcards', 
            'r/footballcards',
            'r/hockeycards',
            'r/pokemontcg',
            'r/tradingcards',
            'r/sportscards',
            'r/cardinvesting'
        ],
        'content_types': [
            'hot_posts',
            'new_posts',
            'top_posts',
            'comments',
            'user_activity'
        ]
    }
    
    discussion_analysis = setup_discussion_analysis(reddit_config)
    
    return initialize_reddit_monitoring(reddit_config, discussion_analysis)
```

## Database Integration & Storage

### PostgreSQL Setup for Card Data
```sql
-- Trading Card Database Schema

-- Cards master table
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    brand VARCHAR(100) NOT NULL,
    set_name VARCHAR(200) NOT NULL,
    player_name VARCHAR(200) NOT NULL,
    card_number VARCHAR(50),
    parallel_type VARCHAR(100),
    rookie_card BOOLEAN DEFAULT FALSE,
    sport VARCHAR(50) NOT NULL,
    team VARCHAR(100),
    position VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Graded cards table
CREATE TABLE graded_cards (
    id SERIAL PRIMARY KEY,
    card_id INTEGER REFERENCES cards(id),
    grading_service VARCHAR(20) NOT NULL, -- PSA, BGS, SGC
    grade VARCHAR(10) NOT NULL,
    cert_number VARCHAR(100) UNIQUE,
    pop_count INTEGER,
    pop_higher INTEGER,
    grade_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Market prices table
CREATE TABLE market_prices (
    id SERIAL PRIMARY KEY,
    card_id INTEGER REFERENCES cards(id),
    grading_service VARCHAR(20),
    grade VARCHAR(10),
    sale_price DECIMAL(10,2) NOT NULL,
    sale_date DATE NOT NULL,
    platform VARCHAR(50) NOT NULL, -- eBay, COMC, PWCC, etc.
    sale_type VARCHAR(20), -- auction, buy_it_now
    listing_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Portfolio tracking table
CREATE TABLE portfolio_holdings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    card_id INTEGER REFERENCES cards(id),
    graded_card_id INTEGER REFERENCES graded_cards(id),
    purchase_price DECIMAL(10,2) NOT NULL,
    purchase_date DATE NOT NULL,
    current_value DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'held', -- held, listed, sold
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Market intelligence cache
CREATE TABLE market_intelligence (
    id SERIAL PRIMARY KEY,
    card_id INTEGER REFERENCES cards(id),
    intelligence_type VARCHAR(50) NOT NULL, -- price_trend, population_change, etc.
    data_point JSONB NOT NULL,
    confidence_score DECIMAL(3,2),
    data_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_cards_player_year ON cards(player_name, year);
CREATE INDEX idx_cards_sport_year ON cards(sport, year);
CREATE INDEX idx_market_prices_date ON market_prices(sale_date);
CREATE INDEX idx_market_prices_card_grade ON market_prices(card_id, grade);
CREATE INDEX idx_portfolio_user ON portfolio_holdings(user_id);
CREATE INDEX idx_market_intelligence_card ON market_intelligence(card_id, data_date);
```

### MongoDB Setup for Unstructured Data
```javascript
// MongoDB collections for flexible data storage

// Social media mentions collection
db.social_mentions.createIndex({ "timestamp": 1, "platform": 1 });
db.social_mentions.createIndex({ "player_name": 1, "sentiment": 1 });

// Market trends collection  
db.market_trends.createIndex({ "date": 1, "category": 1 });
db.market_trends.createIndex({ "trend_type": 1, "confidence": 1 });

// Competitor intelligence collection
db.competitor_data.createIndex({ "competitor_id": 1, "date": 1 });
db.competitor_data.createIndex({ "data_type": 1, "category": 1 });

// Example document structures
const socialMentionSchema = {
  _id: ObjectId(),
  platform: "twitter", // twitter, reddit, instagram, youtube
  post_id: "1234567890",
  author: "cardcollector123",
  content: "Just pulled a PSA 10 Luka rookie!",
  timestamp: ISODate("2026-03-10T12:00:00Z"),
  player_name: "Luka Doncic",
  card_mentioned: {
    year: 2018,
    brand: "Panini",
    set: "Prizm",
    card_type: "rookie"
  },
  sentiment: 0.8, // -1 to 1
  engagement: {
    likes: 45,
    shares: 12,
    comments: 8
  }
};

const marketTrendSchema = {
  _id: ObjectId(),
  date: ISODate("2026-03-10T00:00:00Z"),
  category: "basketball_rookies",
  trend_type: "price_movement",
  data: {
    average_change: 0.15,
    volume_change: 0.25,
    top_movers: [
      { player: "Victor Wembanyama", change: 0.35 },
      { player: "Scoot Henderson", change: 0.22 }
    ]
  },
  confidence: 0.85,
  source: "ebay_sales_analysis"
};
```

## Notification & Alert Systems

### Discord Integration
```python
def setup_discord_notifications(webhook_url, notification_config):
    """
    Discord webhook integration for market alerts and daily briefings
    """
    discord_config = {
        'webhook_url': webhook_url,
        'notification_types': {
            'price_alerts': {
                'threshold': notification_config['price_change_threshold'],
                'format': 'embed',
                'color': 0xFF5733,
                'frequency': 'immediate'
            },
            'daily_briefings': {
                'schedule': notification_config['briefing_schedule'],
                'format': 'rich_embed',
                'color': 0x3498DB,
                'frequency': 'daily'
            },
            'opportunity_alerts': {
                'confidence_threshold': notification_config['opportunity_confidence'],
                'format': 'embed_with_buttons',
                'color': 0x2ECC71,
                'frequency': 'as_needed'
            }
        }
    }
    
    return initialize_discord_client(discord_config)
```

### Email Notification System
```python
def setup_email_notifications(smtp_config, email_templates):
    """
    SMTP email integration for detailed reports and alerts
    """
    email_config = {
        'smtp_server': smtp_config['server'],
        'smtp_port': smtp_config['port'],
        'username': smtp_config['username'],
        'password': smtp_config['password'],
        'encryption': smtp_config['encryption'], # TLS/SSL
        'templates': {
            'daily_briefing': email_templates['daily_briefing'],
            'weekly_report': email_templates['weekly_report'],
            'opportunity_alert': email_templates['opportunity_alert'],
            'portfolio_update': email_templates['portfolio_update']
        }
    }
    
    return configure_email_client(email_config)
```

## Custom Integration Development

### REST API Wrapper Creation
```python
def create_custom_api_wrapper(api_spec, integration_config):
    """
    Generic API wrapper generator for custom integrations
    """
    class CustomAPIWrapper:
        def __init__(self, base_url, auth_config, rate_limits):
            self.base_url = base_url
            self.auth = self._setup_authentication(auth_config)
            self.rate_limiter = self._setup_rate_limiting(rate_limits)
            self.session = self._create_session()
        
        def _setup_authentication(self, auth_config):
            auth_type = auth_config.get('type')
            if auth_type == 'bearer_token':
                return {'Authorization': f"Bearer {auth_config['token']}"}
            elif auth_type == 'api_key':
                return {auth_config['header']: auth_config['key']}
            elif auth_type == 'oauth2':
                return self._setup_oauth2(auth_config)
            return {}
        
        def _setup_rate_limiting(self, rate_limits):
            from time import sleep
            import threading
            
            def rate_limiter(calls_per_second=1):
                def decorator(func):
                    last_called = [0.0]
                    lock = threading.Lock()
                    
                    def wrapper(*args, **kwargs):
                        with lock:
                            elapsed = time.time() - last_called[0]
                            left_to_wait = 1.0 / calls_per_second - elapsed
                            if left_to_wait > 0:
                                sleep(left_to_wait)
                            ret = func(*args, **kwargs)
                            last_called[0] = time.time()
                            return ret
                    return wrapper
                return decorator
            
            return rate_limiter(rate_limits.get('calls_per_second', 1))
        
        @rate_limiter
        def make_request(self, endpoint, method='GET', params=None, data=None):
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=self.auth
            )
            response.raise_for_status()
            return response.json()
    
    return CustomAPIWrapper(
        integration_config['base_url'],
        integration_config['auth'],
        integration_config['rate_limits']
    )
```

### Webhook Processing System
```python
def setup_webhook_processing(webhook_config, processing_handlers):
    """
    Webhook processing system for real-time data integration
    """
    from flask import Flask, request, jsonify
    import hmac
    import hashlib
    
    app = Flask(__name__)
    
    def verify_webhook_signature(payload, signature, secret):
        """Verify webhook signature for security"""
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    @app.route('/webhooks/ebay', methods=['POST'])
    def handle_ebay_webhook():
        signature = request.headers.get('X-EBAY-SIGNATURE')
        if not verify_webhook_signature(request.data, signature, webhook_config['ebay_secret']):
            return jsonify({'error': 'Invalid signature'}), 401
        
        data = request.json
        processing_handlers['ebay'](data)
        return jsonify({'status': 'processed'})
    
    @app.route('/webhooks/psa', methods=['POST'])
    def handle_psa_webhook():
        signature = request.headers.get('X-PSA-SIGNATURE')
        if not verify_webhook_signature(request.data, signature, webhook_config['psa_secret']):
            return jsonify({'error': 'Invalid signature'}), 401
        
        data = request.json
        processing_handlers['psa'](data)
        return jsonify({'status': 'processed'})
    
    return app
```

## Data Pipeline Configuration

### ETL Pipeline Setup
```python
def setup_data_pipeline(source_configs, transformation_rules, target_config):
    """
    Comprehensive ETL pipeline for trading card data processing
    """
    import pandas as pd
    from sqlalchemy import create_engine
    
    class TradingCardETL:
        def __init__(self, sources, transforms, target):
            self.sources = sources
            self.transforms = transforms  
            self.target = target
            self.engine = create_engine(target['connection_string'])
        
        def extract_ebay_data(self):
            """Extract sold listing data from eBay"""
            ebay_api = self.sources['ebay']['client']
            
            sold_listings = []
            for category in self.sources['ebay']['categories']:
                listings = ebay_api.get_sold_listings(
                    category_id=category,
                    days_back=7,
                    limit=1000
                )
                sold_listings.extend(listings)
            
            return pd.DataFrame(sold_listings)
        
        def extract_social_data(self):
            """Extract social media mentions and sentiment"""
            twitter_api = self.sources['twitter']['client']
            reddit_api = self.sources['reddit']['client']
            
            social_data = []
            
            # Twitter mentions
            twitter_mentions = twitter_api.search_mentions(
                keywords=self.sources['twitter']['keywords'],
                days_back=1
            )
            social_data.extend(twitter_mentions)
            
            # Reddit discussions
            reddit_discussions = reddit_api.get_discussions(
                subreddits=self.sources['reddit']['subreddits'],
                days_back=1
            )
            social_data.extend(reddit_discussions)
            
            return pd.DataFrame(social_data)
        
        def transform_price_data(self, raw_data):
            """Clean and normalize price data"""
            # Remove outliers
            Q1 = raw_data['price'].quantile(0.25)
            Q3 = raw_data['price'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            clean_data = raw_data[
                (raw_data['price'] >= lower_bound) & 
                (raw_data['price'] <= upper_bound)
            ]
            
            # Normalize card names
            clean_data['player_name'] = clean_data['player_name'].str.title()
            clean_data['brand'] = clean_data['brand'].str.upper()
            
            return clean_data
        
        def load_to_database(self, processed_data, table_name):
            """Load processed data to PostgreSQL"""
            processed_data.to_sql(
                table_name,
                self.engine,
                if_exists='append',
                index=False,
                method='multi'
            )
        
        def run_pipeline(self):
            """Execute complete ETL pipeline"""
            # Extract
            ebay_data = self.extract_ebay_data()
            social_data = self.extract_social_data()
            
            # Transform
            clean_ebay_data = self.transform_price_data(ebay_data)
            processed_social_data = self.transform_social_data(social_data)
            
            # Load
            self.load_to_database(clean_ebay_data, 'market_prices')
            self.load_to_database(processed_social_data, 'social_mentions')
            
            return {
                'ebay_records': len(clean_ebay_data),
                'social_records': len(processed_social_data),
                'status': 'success'
            }
    
    return TradingCardETL(source_configs, transformation_rules, target_config)
```

## Monitoring & Maintenance

### Integration Health Monitoring
```python
def setup_integration_monitoring(integrations, monitoring_config):
    """
    Monitor the health and performance of all integrations
    """
    import time
    import threading
    from dataclasses import dataclass
    from typing import Dict, List
    
    @dataclass
    class IntegrationHealth:
        name: str
        status: str  # healthy, degraded, down
        last_check: float
        response_time: float
        error_count: int
        success_rate: float
    
    class IntegrationMonitor:
        def __init__(self, integrations, config):
            self.integrations = integrations
            self.config = config
            self.health_status = {}
            self.monitoring_active = False
        
        def check_integration_health(self, integration_name, integration_client):
            """Check health of individual integration"""
            start_time = time.time()
            try:
                # Perform health check based on integration type
                if hasattr(integration_client, 'health_check'):
                    result = integration_client.health_check()
                else:
                    # Default health check - make simple API call
                    result = integration_client.get_status()
                
                response_time = time.time() - start_time
                
                self.health_status[integration_name] = IntegrationHealth(
                    name=integration_name,
                    status='healthy',
                    last_check=time.time(),
                    response_time=response_time,
                    error_count=0,
                    success_rate=1.0
                )
                
            except Exception as e:
                response_time = time.time() - start_time
                
                current_health = self.health_status.get(integration_name)
                error_count = (current_health.error_count + 1) if current_health else 1
                
                self.health_status[integration_name] = IntegrationHealth(
                    name=integration_name,
                    status='down' if error_count > 3 else 'degraded',
                    last_check=time.time(),
                    response_time=response_time,
                    error_count=error_count,
                    success_rate=0.0
                )
                
                # Send alert for failed integration
                self.send_integration_alert(integration_name, str(e))
        
        def monitor_continuously(self):
            """Run continuous monitoring in background thread"""
            def monitoring_loop():
                while self.monitoring_active:
                    for name, client in self.integrations.items():
                        self.check_integration_health(name, client)
                    
                    time.sleep(self.config['check_interval'])
            
            self.monitoring_active = True
            monitoring_thread = threading.Thread(target=monitoring_loop)
            monitoring_thread.daemon = True
            monitoring_thread.start()
        
        def get_health_report(self):
            """Generate comprehensive health report"""
            return {
                'overall_status': self.calculate_overall_status(),
                'integrations': dict(self.health_status),
                'generated_at': time.time()
            }
        
        def send_integration_alert(self, integration_name, error_message):
            """Send alert when integration fails"""
            alert_message = f"🚨 Integration Alert: {integration_name} is experiencing issues\nError: {error_message}"
            
            # Send to configured notification channels
            if 'discord' in self.config['alert_channels']:
                self.send_discord_alert(alert_message)
            if 'email' in self.config['alert_channels']:
                self.send_email_alert(integration_name, error_message)
    
    return IntegrationMonitor(integrations, monitoring_config)
```

### Automated Maintenance Tasks
```python
def setup_automated_maintenance(maintenance_config, database_config):
    """
    Automated maintenance tasks for optimal system performance
    """
    import schedule
    import time
    import threading
    
    class MaintenanceManager:
        def __init__(self, config, db_config):
            self.config = config
            self.db_config = db_config
            self.maintenance_active = False
        
        def cleanup_old_data(self):
            """Clean up old data based on retention policies"""
            from sqlalchemy import create_engine, text
            
            engine = create_engine(self.db_config['connection_string'])
            
            cleanup_queries = [
                # Remove old price data (keep 2 years)
                "DELETE FROM market_prices WHERE sale_date < NOW() - INTERVAL '2 years'",
                
                # Remove old social mentions (keep 6 months)
                "DELETE FROM social_mentions WHERE created_at < NOW() - INTERVAL '6 months'",
                
                # Archive old portfolio transactions
                """
                INSERT INTO portfolio_archive 
                SELECT * FROM portfolio_holdings 
                WHERE updated_at < NOW() - INTERVAL '1 year'
                """,
                
                # Clean up temporary cache tables
                "DELETE FROM market_intelligence WHERE created_at < NOW() - INTERVAL '30 days'"
            ]
            
            with engine.connect() as conn:
                for query in cleanup_queries:
                    conn.execute(text(query))
                    conn.commit()
        
        def update_market_data(self):
            """Refresh market data and calculations"""
            # Update population counts from PSA
            self.refresh_population_data()
            
            # Recalculate market trends
            self.recalculate_market_trends()
            
            # Update portfolio valuations
            self.update_portfolio_values()
        
        def optimize_database(self):
            """Optimize database performance"""
            from sqlalchemy import create_engine, text
            
            engine = create_engine(self.db_config['connection_string'])
            
            optimization_queries = [
                "ANALYZE;",  # Update table statistics
                "VACUUM ANALYZE;",  # Reclaim space and update stats
                "REINDEX DATABASE trading_cards;"  # Rebuild indexes
            ]
            
            with engine.connect() as conn:
                for query in optimization_queries:
                    conn.execute(text(query))
        
        def generate_backup(self):
            """Create database backup"""
            import subprocess
            import datetime
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"trading_cards_backup_{timestamp}.sql"
            
            subprocess.run([
                'pg_dump',
                '-h', self.db_config['host'],
                '-U', self.db_config['username'],
                '-d', self.db_config['database'],
                '-f', backup_file
            ])
        
        def start_maintenance_scheduler(self):
            """Start automated maintenance scheduler"""
            # Daily maintenance tasks
            schedule.every().day.at("02:00").do(self.cleanup_old_data)
            schedule.every().day.at("03:00").do(self.update_market_data)
            
            # Weekly maintenance tasks  
            schedule.every().sunday.at("01:00").do(self.optimize_database)
            schedule.every().sunday.at("04:00").do(self.generate_backup)
            
            def run_scheduler():
                while self.maintenance_active:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
            
            self.maintenance_active = True
            scheduler_thread = threading.Thread(target=run_scheduler)
            scheduler_thread.daemon = True
            scheduler_thread.start()
    
    return MaintenanceManager(maintenance_config, database_config)
```