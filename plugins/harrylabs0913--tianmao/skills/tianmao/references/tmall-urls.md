# Tmall (天猫) URLs Reference

## Official Domains

### Primary Domain
- **https://www.tmall.com** - Main Tmall website (global)
- **https://www.tmall.hk** - Hong Kong version
- **https://www.tmall.cn** - China mainland version (may redirect)

### Alternative/Synonym Domains
- **https://www.tianmao.com** - "Tianmao" pinyin domain (redirects to tmall.com)
- **https://tmall.com** - Shorter version (redirects to www.tmall.com)

### Mobile Sites
- **https://m.tmall.com** - Mobile-optimized version
- **https://h5.m.tmall.com** - HTML5 mobile version

### Special Sections
- **https://www.tmall.com/wow** - Tmall Wow (brand promotions)
- **https://ju.tmall.com** - Tmall Ju (group buying/deals)
- **https://chaoshi.tmall.com** - Tmall Supermarket (groceries)
- **https://travel.tmall.com** - Tmall Travel
- **https://www.tmall.com/global** - Tmall Global (cross-border e-commerce)

## Regional Variations

### China Mainland
- Primary: `www.tmall.com` (自动根据IP跳转到大陆版)
- Often requires login via Taobao/Tmall account

### International
- `www.tmall.hk` - English interface, international shipping
- `www.tmall.com` with region selector

## URL Patterns for Common Actions

### Search
```
https://list.tmall.com/search_product.htm?q={query}
```

### Product Page
```
https://detail.tmall.com/item.htm?id={product_id}
```

### Category
```
https://list.tmall.com/search_cat.htm?cat={category_id}
```

### Seller Store
```
https://{shopname}.tmall.com
```

## Security Notes

### Verified URLs
Always use `https://` (not http) for security. The official Tmall sites have valid SSL certificates.

### Phishing Warning
Be cautious of:
- Misspellings: `tma11.com`, `tmaII.com` (using numbers/letters that look similar)
- Extra subdomains: `tmall-login.com`, `tmall-security.com` (not official)
- HTTP only sites (should always be HTTPS)

### Official Verification
To verify you're on the real Tmall:
1. Check the SSL certificate (should be issued to `*.tmall.com`)
2. Look for the official Tmall/Alibaba logo in the footer
3. The URL should be exactly `tmall.com` or `tianmao.com` (no extra words)

## Historical Context

- **2008**: Tmall launched as Taobao Mall
- **2011**: Rebranded as Tmall (天猫)
- **2014**: Tmall Global launched for international brands
- **2020**: Tmall Luxury Pavilion launched for luxury goods

The name "天猫" (Tiānmāo) means "Heavenly Cat" in Chinese, a play on "cat" being lucky in Chinese culture and the "mall" concept.