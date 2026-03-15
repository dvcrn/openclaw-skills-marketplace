# Solscan API - Frequently Asked Questions

> This document contains comprehensive FAQ for Solscan API, including account management, API usage, and technical details.

---

## Table of Contents

1. [Account Creation and Subscription](#account-creation-and-subscription)
2. [API Key Navigation and Management](#api-key-navigation-and-management)
3. [Functional Questions](#functional-questions)
4. [Data Coverage](#data-coverage)

---

## Account Creation and Subscription

### 1. How do I create a Solscan account?

To create a Solscan account, visit [solscan.io](https://solscan.io). You can sign up by providing your email address and setting a password. Once registered, you can log in to access your Solscan API Management usage dashboard. This is the starting point for all Pro API interactions.

---

### 2. How do I subscribe to a Solscan Pro API plan?

Navigate to the "Resources" section on [solscan.io](https://solscan.io) and click "API Plans." You will be redirected to the Solscan Pro API landing page where you can select a plan and subscription period (e.g., monthly or longer-term). Proceed to the Stripe checkout page to enter payment details and confirm. For cryptocurrency payments with a minimum 6-month commitment, email [support@solscan.io](mailto:support@solscan.io). After payment confirmation, your subscription is active.

---

### 3. Do top-up CUs roll over to the next billing cycle?

No. Top-up CUs do not roll over to the next billing cycle. All top-up CUs are valid only for the current billing period and will expire at the end of that cycle if unused. 
If you expect higher usage on a recurring basis, we recommend upgrading your plan instead of relying on top-ups.

---

### 4. What payment methods are supported?

Subscriptions primarily use Stripe for credit card payments. For cryptocurrency options, contact support with a minimum 6-month commitment. All payments are subject to the Solscan API Payment Terms and Conditions.

---

### 5. What plans are available for Solscan Pro API?

Specific plan details, including tiers, pricing, and features, are available on the API Plans page at [solscan.io/apis](https://solscan.io/apis). Plans are structured around Computing Units (CU) for API usage, with all CU set to 100. For custom options or detailed levels, contact [support@solscan.io](mailto:support@solscan.io) to register, as standard plans may not be publicly listed in full detail without login.

---

### 6. Can I get a refund for my API plan?

No, refunds are not offered for any API plans once the purchase is completed. Cancellations do not result in reimbursement, per the terms and conditions.

---

### 7. What if my payment fails or is delayed?

If payment fails during checkout, verify your details on the Stripe page and try again. For delays in confirmation, check your email for status updates or contact [support@solscan.io](mailto:support@solscan.io). Once confirmed, access your profile to proceed with API setup.

---

### 8. Why is my API account not activated after I made a payment?

If your API account remains inactive after payment, follow these steps:

- Check your profile and navigate to the API management section in your dashboard. Click "Activate my API key" to enable your API access.
- If the issue persists after activation, contact our support team at [support@solscan.io](mailto:support@solscan.io) for assistance. Please attempt activation before contacting support.

---

### 9. How do I manage my Pro API subscription?

Solscan Pro API uses a subscription-based model and sends billing emails based on your selected package. You can track your API usage through the dashboard, which shows detailed consumption metrics. To customize your package or discuss specific needs, contact our support team at [support@solscan.io](mailto:support@solscan.io).

---

## API Key Navigation and Management

### 1. How do I use my API key?

After subscribing and confirming payment, navigate to your Profile page on [solscan.io](https://solscan.io) and select API Management. Copy the unique key and include it in the request header of your code (e.g., as an Authorization header) when making API calls.

---

### 2. How do I change my API key?

In the API Management section of your profile, select "Rotate Your API Key" to generate a new one. Note that once changed, you cannot revert to the old key, so update it in all your applications immediately.

---

### 3. What should I do if my API key is compromised?

Immediately rotate (regenerate) your API key in the API Management section to invalidate the old one. Monitor your API usage for unauthorized activity via your dashboard. Update the new key in your applications and consider contacting [support@solscan.io](mailto:support@solscan.io) if you suspect breach-related issues. As a best practice, treat API keys like passwords and avoid sharing them.

---

## Functional Questions

### 1. What data points are available through the Solscan Pro API?

The API provides comprehensive datasets across categories including:

- Accounts (transfers, token accounts, DeFi activities, balance changes, transactions, staking, rewards)
- Tokens (transfers, DeFi activities, markets, lists, trending, prices, holders, metadata)
- NFTs (new NFTs, activities, collection lists, collection items)
- Transactions (actions, details)
- Blocks (last blocks, details, transactions)
- Chain Information (overall chain stats)
- Markets (token markets, listings)

These endpoints support querying historical and real-time Solana data with filters for precision.

---

### 2. What are the endpoints in "Account" API? What is the specific function of each endpoint?

The Account API offers endpoints for detailed insights into Solana accounts:

- **/v2.0/account/transfer** (GET): Retrieves transfer details. Parameters include address (required), from_time/to_time (optional timestamps), limit/offset (pagination, max 50)
- **/v2.0/account/token-accounts** (GET): Lists token/NFT accounts linked to an address
- **/v2.0/account/defi/activities** (GET): Filters indexed DeFi activities
- **/v2.0/account/balance_change** (GET): Tracks balance changes
- **/v2.0/account/transactions** (GET): Lists all transactions
- **/v2.0/account/exportTransactions** (GET): Exports transaction data in CSV
- **/v2.0/account/stake** (GET): Provides staking details
- **/v2.0/account/detail** (GET): Returns account info
- **/v2.0/account/reward/export** (GET): Exports reward history in CSV

---

### 3. What are the endpoints in "Token" API? What is the specific function of each endpoint?

The Token API provides:

- **/v2.0/token/transfer**: Filters transfers by action type/amount
- **/v2.0/token/defi/activities**: DeFi activities related to token
- **/v2.0/token/markets**: Market information
- **/v2.0/token/list**: Lists tokens (sortable by creation date or market cap, up to 50,000 items)
- **/v2.0/token/trending**: Shows trending tokens
- **/v2.0/token/price**: Retrieves historical or current price
- **/v2.0/token/holders**: Lists top holders
- **/v2.0/token/meta**: Gets metadata like name, symbol, supply

---

### 4. What are the endpoints in "NFT" API? What is the specific function of each endpoint?

The NFT API focuses on NFT data:

- **/v2.0/nft/new**: Lists newly created NFTs
- **/v2.0/nft/activities**: Indexes NFT actions such as mint or sale
- **/v2.0/nft/collection/lists**: Lists NFT collections
- **/v2.0/nft/collection/items**: Provides trading data for items in a collection

---

### 5. What are the endpoints in "Transaction" API? What is the specific function of each endpoint?

The Transaction API provides:

- **/v2.0/transaction/actions**: Overview of transaction activities with parsed instructions
- **/v2.0/transaction/detail**: Detailed parsed data for a transaction including balance changes, token transfers, and fees

---

### 6. Why can't I get the pricing data of newly created tokens?

The API supports pricing data for all Solana tokens, including newly created ones, via the /token/price endpoint. However, there may be a 3-minute delay for validation and accuracy.

---

### 7. What is the transaction history available for the most used Solscan Pro API endpoints?

History varies by endpoint:

- Transfer endpoints (e.g., /account/transfer, /token/transfer) offer up to 3 years (from July 2021)
- Balance Change and DeFi Activities provide 6 months of historical data

Other endpoints may support full historical data depending on parameters.

---

### 8. What is the delay in token price and market cap data?

Token price and market cap data have a 3-minute delay to ensure reliability through validation processes, applicable to endpoints like /token/price and /token/markets.

---

### 9. What tokens does the token list endpoint include?

The /token/list endpoint covers up to 50,000 tokens, including the top 2,000 by market capitalization, with filtering and sorting options for creation date, volume, or other metrics.

---

### 10. Does the Solscan Pro API cover the testnet?

No, the API exclusively supports the Solana mainnet and has no current plans for testnet integration.

---

### 11. What are the endpoints in "Block" API? What is the specific function of each endpoint?

The Block API provides blockchain block data:

- **/v2.0/block/last**: Retrieves the last blocks (max 20 per request)
- **/v2.0/block/detail**: Gets detailed info for a block
- **/v2.0/block/transactions**: Lists transactions in a block

---

### 12. What are the endpoints in "Chain" and "Market" APIs?

Chain API:
- **/v2.0/chaininfo**: Provides overall chain information such as total supply, TPS, and validator count

Market API:
- **/v2.0/market/list**: Lists token markets/pools
- **/v2.0/market/token**: Gets market data for a specific token

---

### 13. What are the rate limits for the API?

Rate limits are managed via Computing Units (CU), with each endpoint consuming 100 CU per request in V2.0. Limits depend on your subscription plan; exceedances return errors. Monitor usage via the /monitor/usage endpoint.

---

### 14. What are the Rate Limits and CU Limits for each Solscan API plan?

The Rate Limit (requests per minute) and Compute Unit (CU) Limit (per month) vary depending on your subscription tier. Below is the breakdown for each plan:

- **Solscan Free API:** CU Limit: 10,000,000 CU / Month, Rate Limit: 1,000 Requests / 60 seconds
- **Solscan Pro API Level 2:** CU Limit: 150,000,000 CU / Month, Rate Limit: 1,000 Requests / 60 seconds
- **Solscan Pro API Level 3:** CU Limit: 500,000,000 CU / Month, Rate Limit: 2,000 Requests / 60 seconds
- **Solscan Pro API Level 4:** CU Limit: 1,500,000,000 CU / Month, Rate Limit: 3,000 Requests / 60 seconds

---

### 15. How can I monitor my Pro API usage?

You can easily track your current API usage through the **Solscan Pro API Dashboard**. Log in to your Solscan account and navigate to your **Profile** page & **API Management** section. The dashboard provides real-time insights into your consumption, allowing you to track how many Compute Units (CUs) you have used against your monthly quota. This helps ensure you stay within your plan's limits and allows you to manage your integration effectively.

---

### 16. How do I authenticate API requests?

Include your API key in the Authorization header as 'Bearer ' for all requests. Use V2 keys for V2.0 endpoints; authentication is required for all Pro API calls.

---

### 17. What are common error types and how to handle them?

Common errors include:

- 1100 (Validation Error) – invalid parameters
- 429 (Rate Limit Exceeded) – reduce frequency or upgrade plan
- 401 (Unauthorized) – verify API key

Handle by parsing error codes/messages and retrying with corrections.

---

### 18. Is there a Postman collection or sample code?

Yes, a Pro API Postman Collection is available for testing all V2.0 endpoints. Download from the docs or generate requests by adding your key. Sample code snippets (e.g., Python, JS) are provided in the reference docs.

---

## Data Coverage

### API Coverage & Program Map

#### 1. Endpoint Classification

Solscan Pro API offers a set of endpoints that serves the particular nature of Solana Blockchain data. Below are the breakdown of all Solscan Pro API endpoints into different categories of data groups:

##### Raw

- **Block:** `block/last`, `block/transactions`, `block/detail`
- **Transaction:** `transaction/last`, `transaction/detail`, `transaction/detail/multi`, `transaction/fees`
- **Account:** `account/detail`, `account/transfer`, `account/transactions`, `account/balance_change`, `account/token-accounts`, `account/portfolio`, `account/metadata`, `account/leaderboard`
- **Token:** `token/list`, `token/transfer`, `token/holders`, `token/meta`, `token/top`, `token/trending`, `token/latest`

##### Decoded

- **Transaction:** `transaction/actions` (Decoded), `transaction/actions/multi`
- **Account:** `account/data-decoded`, `account/defi/activities` (and Export), `account/transfer/export`
- **Token:** `token/defi/activities` (and Export)

##### Staking

- **Account:** `account/stake`, `account/reward/export`

##### Dex Trading

- **Market:** `market/list` (Listing Pool/Market), `market/info`, `market/volume` (Historical market data)
- **Token:** `token/markets`

##### Lending

- Access via `account/defi/activities` or `token/defi/activities` filtered by Lending programs

##### Market

- **Token:** `token/price`, `token/price/multi`, `token/historical-data`

##### NFT

- **NFT:** `nft/news` (New NFT), `nft/activities`, `nft/collection/lists`, `nft/collection/items`

#### 2. Project Map (Program Coverage)

This map categorizes the supported programs/projects into the functional verticals (Dex Trading, Lending, Staking, NFT) based on the Solscan Pro API coverage.

##### DEX Trading

*Coverage of Spot, Swap, Perps, and Aggregators.*

- **Jupiter:** Jupiter Aggregator (v1-v6), Jupiter DCA, Jupiter Limit Order (v1-v2), Jupiter Perpetuals, Jupiter Lock
- **Raydium:** Raydium AMM, Raydium CLMM, Raydium CPMM, Raydium IDO, Raydium Liquidity Pool (v2-v4), Raydium Stake
- **Orca:** Orca Token Swap (v1-v2), Orca Aquafarm, Whirlpools Program
- **Meteora:** Meteora DLMM, Meteora Pools, Meteora Vault, Mercurial Dynamic AMM, Mercurial Stable Swap
- **OpenBook:** OpenBook, Openbook V2
- **Pump.fun:** Pump.fun, Pump.fun AMM
- **Lifinity:** Lifinity Swap (v1-v2)
- **Saber:** Saber Router, Saber Stable Swap, Saber Decimal Wrapper
- **Phoenix:** Phoenix
- **Fluxbeam:** Fluxbeam Program
- **Aldrin:** Aldrin AMM (v1-v2), Aldrin DTWap
- **StepN:** StepN DOOAR Swap
- **Saros:** Saros AMM
- **Mango:** Mango Markets (v1-v4)
- **Drift:** Drift V2 Program
- **Zeta:** Zeta DEX
- **Others:** 01 Dex, Atrix Finance, BonkSwap, Crema Finance, Cropper Finance, Cykura Swap, Dexlab, Dradex, GooseFX, Guac Swap, Hadeswap, Invariant, Obric V2, OKX DEX, OpenOcean, Penguin Finance, Prism Aggregator, SolFi, Step Finance, ZeroFi

##### Lending

*Coverage of Borrowing, Lending, and Money Markets.*

- **Kamino:** Kamino Lending Program, Kamino Farm
- **Solend:** Solend Protocol
- **Marginfi:** Marginfi, Marginfi V2
- **Port Finance:** Port Finance (v1, Canary)
- **Jet Protocol:** Jet Protocol (Staking, Rewards, Auth)
- **Francium:** Francium Lending, Francium Rewards
- **Tulip:** Tulip Protocol V2 Vaults
- **Hubble:** Hubble Protocol

##### Staking & Yield

*Coverage of Liquid Staking, Stake Pools, and Yield Farming.*

- **Marinade:** Marinade Finance, Marinade Staking, Marinade Bond
- **Jito:** Jito Tip Distribution
- **Lido:** Lido for Solana
- **Sanctum:** Sanctum Router, Sanctum SPL Stake Pool (Multi & Single Validator), Sanctum Flat Fee Pricing
- **Solayer:** Solayer endoAVS, Solayer sUSDC
- **BlazeStake:** (Often covered under Stake Pool Program generic or specific Solblaze IDs)
- **Generic:** Stake Program, Stake Pool Program

##### NFT

*Coverage of Marketplaces, Launchpads, and Utilities.*

- **Magic Eden:** Magic Eden V2, Magic Eden NFT Marketplace, Magic Eden cNFT, MagicEden AMM
- **Tensor:** Tensor Swap, Tensor cNFT, Tensor Whitelist
- **Metaplex:** Metaplex Token Metadata, Candy Machine (v1-v2), Auction House, Bubblegum (cNFT), Token Auth Rules
- **Solanart:** Solanart NFT Marketplace
- **Hadeswap:** Hadeswap
- **Mooar:** Mooar
- **Others:** Bonfida Name Service, AllDomains (Name Service/TLD), Cardinal (if applicable), Star Atlas Marketplace

---

## Support

For additional questions or support, please contact:

- **Email:** [support@solscan.io](mailto:support@solscan.io)
- **Website:** [https://solscan.io](https://solscan.io)
- **API Documentation:** [https://docs.solscan.io](https://docs.solscan.io)

---

*Last updated: 2026-03-12*