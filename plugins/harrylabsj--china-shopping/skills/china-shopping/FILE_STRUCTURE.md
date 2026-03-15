# File Structure

## Complete Directory Layout

```
~/.openclaw/workspace/skills/china-shopping/
│
├── SKILL.md                    # Skill definition document
├── COMMAND_DESIGN.md           # Command design specifications  
├── RECOMMENDATION_LOGIC.md     # Recommendation algorithm design
├── TECHNICAL_IMPLEMENTATION.md # Technical implementation details
├── FILE_STRUCTURE.md           # This file
│
├── china-shopping              # Main executable script (Bash)
│
├── data/                       # All data files
│   ├── categories.json         # Category definitions & website recommendations
│   ├── product_mapping.json    # Product-to-category mapping
│   ├── websites.json           # Website metadata & descriptions
│   └── general_fallback.json   # Fallback recommendations
│
├── lib/                        # Library scripts
│   ├── recommend.sh            # Main recommendation logic
│   ├── match.sh               # Product matching functions
│   ├── format.sh              # Output formatting
│   ├── utils.sh               # Utility functions
│   └── config.sh              # Configuration loading
│
├── config/                     # Configuration files
│   ├── defaults.conf          # Default settings
│   └── user_preferences.conf  # User preferences (optional)
│
├── logs/                       # Log directory
│   ├── access.log             # Usage logs
│   └── error.log              # Error logs
│
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   │   ├── test_match.sh
│   │   ├── test_recommend.sh
│   │   └── test_format.sh
│   ├── integration/           # Integration tests
│   │   └── test_cli.sh
│   └── test_data/             # Test data
│       └── sample_products.txt
│
├── examples/                   # Usage examples
│   ├── basic_usage.sh
│   ├── chat_integration.md
│   └── output_samples/
│       ├── electronics.txt
│       ├── clothing.txt
│       └── groceries.txt
│
├── docs/                       # Documentation
│   ├── API.md                 # API documentation (future)
│   ├── CHANGELOG.md           # Version history
│   ├── CONTRIBUTING.md        # Contribution guidelines
│   └── FAQ.md                 # Frequently asked questions
│
└── scripts/                    # Maintenance scripts
    ├── install.sh             # Installation script
    ├── update_data.sh         # Data update script
    ├── backup.sh              # Backup script
    └── uninstall.sh           # Uninstallation script
```

## File Descriptions

### Core Files

1. **SKILL.md** - Primary skill documentation
   - Skill overview and description
   - Trigger phrases and usage examples
   - Installation and configuration instructions
   - Author and license information

2. **china-shopping** - Main executable
   - Entry point for all commands
   - Command-line argument parsing
   - Subcommand routing
   - Error handling and help display

### Data Files (JSON Format)

3. **data/categories.json** - Category definitions
   ```json
   {
     "electronics": {
       "name": "电子产品",
       "description": "手机、电脑、数码产品等",
       "websites": [...],
       "shopping_tips": [...],
       "icon": "📱"
     }
   }
   ```

4. **data/product_mapping.json** - Product-to-category mapping
   ```json
   {
     "手机": "electronics",
     "智能手机": "electronics",
     "衣服": "clothing"
   }
   ```

5. **data/websites.json** - Website metadata
   ```json
   {
     "jd": {
       "name": "京东",
       "url": "https://www.jd.com",
       "description": "中国最大的自营式电商企业",
       "strengths": ["正品", "物流快", "售后好"],
       "weaknesses": ["价格可能较高"]
     }
   }
   ```

6. **data/general_fallback.json** - Fallback recommendations
   - Used when product not found in specific categories
   - General e-commerce platforms (京东, 天猫, 淘宝)

### Library Scripts

7. **lib/recommend.sh** - Recommendation engine
   - Main recommendation logic
   - Category lookup and website selection
   - Ranking and scoring (simple version)

8. **lib/match.sh** - Product matching
   - Product name to category mapping
   - Exact and partial matching
   - Fallback to general category

9. **lib/format.sh** - Output formatting
   - CLI output formatting
   - Chat message formatting
   - JSON output for API (future)

10. **lib/utils.sh** - Utility functions
    - JSON parsing helpers
    - Logging functions
    - Configuration loading

11. **lib/config.sh** - Configuration management
    - Load user preferences
    - Apply default settings
    - Environment variable handling

### Configuration

12. **config/defaults.conf** - Default settings
    ```
    # Default language
    LANGUAGE=zh
    
    # Number of recommendations to show
    RECOMMENDATION_COUNT=4
    
    # Output format
    OUTPUT_FORMAT=text
    
    # Enable/disable logging
    LOGGING_ENABLED=true
    ```

13. **config/user_preferences.conf** - User preferences (optional)
    - User-specific settings
    - Preferred websites per category
    - Price sensitivity settings

### Test Suite

14. **tests/unit/** - Unit tests
    - Test individual functions
    - Mock data for isolated testing
    - Bats test framework compatible

15. **tests/integration/** - Integration tests
    - End-to-end command line tests
    - Verify output formats
    - Test error conditions

### Documentation

16. **docs/** - Additional documentation
    - API documentation for future REST API
    - Changelog for version tracking
    - Contribution guidelines
    - Frequently asked questions

### Examples

17. **examples/** - Usage examples
    - Basic command line usage
    - Integration with chat systems
    - Sample outputs for documentation

### Maintenance Scripts

18. **scripts/install.sh** - Installation script
    - Copy files to correct locations
    - Set executable permissions
    - Create necessary directories

19. **scripts/update_data.sh** - Data update script
    - Update product mappings
    - Refresh website information
    - Add new categories

## File Permissions

```bash
# Main script - executable
chmod 755 china-shopping

# Library scripts - readable
chmod 644 lib/*.sh

# Data files - readable
chmod 644 data/*.json

# Configuration - readable/writable by owner
chmod 600 config/user_preferences.conf
chmod 644 config/defaults.conf

# Log files - writable
chmod 666 logs/*.log 2>/dev/null || true
```

## Environment Variables

The skill checks these environment variables:

- `CHINA_SHOPPING_DATA_DIR`: Override data directory
- `CHINA_SHOPPING_LANG`: Default language (zh/en)
- `CHINA_SHOPPING_FORMAT`: Output format (text/json)
- `CHINA_SHOPPING_DEBUG`: Enable debug logging

## Data File Update Strategy

1. **Versioned data files**: `categories_v1.0.0.json`
2. **Update script**: `scripts/update_data.sh` fetches latest
3. **Backup**: Keep previous version for rollback
4. **Validation**: Verify JSON syntax before use

## Minimal V1.0.0 Structure

For the simple v1.0.0 version, only these files are required:

```
~/.openclaw/workspace/skills/china-shopping/
├── SKILL.md
├── china-shopping
├── data/
│   ├── categories.json
│   └── product_mapping.json
└── lib/
    ├── recommend.sh
    └── utils.sh
```

## Future Expansion Areas

1. **Plugins directory**: `plugins/` for third-party recommendation modules
2. **Cache directory**: `cache/` for API responses and computed results
3. **Localization**: `locales/` for multi-language support
4. **Themes**: `themes/` for different output styles
5. **Extensions**: `extensions/` for browser integration, mobile apps, etc.