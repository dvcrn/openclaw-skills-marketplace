---
name: tradesman-verify
description: "Verify contractor credentials via OpenCorporates business entity lookup (140+ jurisdictions) and Accumulate blockchain identity verification. W3C Verifiable Credentials for contractor license, insurance, and business entity validation."
homepage: https://gitlab.com/lv8rlabs/tradesman-verify
---

# Tradesman Verify Skill

**Contractor verification infrastructure** combining OpenCorporates business entity verification, state licensing board checks, and blockchain-compatible credential attestation for the construction and trades industry.

## Overview

Multi-layer verification for contractors, tradesmen, and service providers:

- **Layer 1**: Business entity verification (OpenCorporates, 140+ jurisdictions)
- **Layer 2**: Professional license validation (state licensing boards)
- **Layer 3**: Compliance verification (optional)
- **Layer 4**: Blockchain attestation (W3C Verifiable Credentials)

## Features

### Business Entity Verification (OpenCorporates)

- Legal business entity exists and is registered
- Company status (Active, Dissolved, Liquidated)
- Incorporation date (business longevity indicator)
- Registered officers and ownership structure
- Business address verification

**Jurisdictions:** United States (all 50 states + DC), United Kingdom, Canada, Australia, and 140+ additional countries.

### State Licensing Board Validation

- Contractor license active status
- License number and business name matching
- Specialty certifications (electrical, plumbing, HVAC, roofing, etc.)
- License expiration date and renewal status

**Coverage:** All 50 US states. Automated checks where state APIs are available; manual verification workflow otherwise.

## Usage

### CLI

```bash
npx tradesman-verify \
  --business-name "ABC Roofing LLC" \
  --jurisdiction "us_tx" \
  --license-number "123456" \
  --state "TX"

# Output
✅ Business Entity Verified
   Company: ABC ROOFING LLC
   Status: Active
   Incorporated: 2020-05-15

✅ Professional License Verified
   License: 123456
   Status: Active
   Expires: 2026-12-31
   Type: General Contractor

✅ VERIFICATION PASSED
   Recommendation: APPROVED
```

### API

```javascript
const { verifyContractor } = require('tradesman-verify');

const result = await verifyContractor({
  businessName: "ABC Roofing LLC",
  jurisdiction: "us_tx",
  licenseNumber: "123456",
  state: "TX"
});

console.log(result.verificationStatus); // "VERIFIED"
console.log(result.recommendation);     // "APPROVED"
```

### Batch Processing

```bash
npx tradesman-verify --batch --input contractors.csv --output report.json

# Processing 15 contractors...
# ✅ 12 verified successfully
# ⚠️  2 require manual review
# ❌ 1 failed verification
```

## Output Format

Verification results follow the W3C Verifiable Credentials data model:

```json
{
  "credentialType": "ContractorVerification",
  "subject": {
    "businessName": "ABC Roofing LLC",
    "jurisdiction": "us_tx",
    "licenseNumber": "123456"
  },
  "verification": {
    "businessEntity": {
      "verified": true,
      "source": "OpenCorporates",
      "status": "Active"
    },
    "professionalLicense": {
      "verified": true,
      "source": "Texas Dept. of Licensing",
      "status": "Active",
      "expiresAt": "2026-12-31T23:59:59Z"
    }
  }
}
```

Compatible with Accumulate ADI credential issuance, Centrifuge proof documents, and W3C Verifiable Credentials.

## Configuration

Requires an OpenCorporates API key. Free tier provides 200 API calls per month — sign up at [opencorporates.com](https://opencorporates.com). Set the key as an environment variable before use.

Premium tiers (automated state license checks, real-time monitoring) require a PPCS API key — see [ppcs.pro](https://ppcs.pro) for details.

## Rate Limits

| Tier | Verifications/Month | Real-Time Monitoring |
|------|---------------------|---------------------|
| **Free** | 50 | No |
| **Pro** | 500 | Yes |
| **Enterprise** | Unlimited | Yes + SLA |

## Roadmap

### Phase 1: Core Verification (Current)
- ✅ OpenCorporates business entity verification
- ✅ Manual state licensing board checks
- ✅ W3C credential-compatible output format
- ✅ Free tier implementation

### Phase 2: Enhanced Automation (Q2 2026)
- 🔄 Automated license check integration (premium tier)
- 🔄 Automated state license checks (all 50 states)
- 🔄 Real-time status change notifications
- 🔄 Premium tier launch

### Phase 3: Blockchain Attestation (Q3 2026)
- 📋 Native Accumulate ADI integration
- 📋 Centrifuge proof document formatting
- 📋 Chainlink oracle integration

### Phase 4: Enhanced Compliance (Q4 2026)
- 📋 Enhanced compliance verification layer
- 📋 Regulatory compliance checks
- 📋 Business continuity monitoring

## Support

- [Source code and issues](https://gitlab.com/lv8rlabs/tradesman-verify)
- [OpenCorporates API Docs](https://api.opencorporates.com/documentation/API-Reference)
- [State license lookup directory](https://licenselookup.org/)

## License

MIT License — free and open source. See LICENSE file for details.

---

**Skill Version**: 2.2.0
**Last Updated**: 2026-03-11
**Maintainer**: TradesmanTools
