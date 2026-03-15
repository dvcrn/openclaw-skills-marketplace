---
name: element-nft
description: "Element Market integration for NFT portfolio and market monitoring. REQUIRES the 'ELEMENT_API_KEY' environment variable. When explicitly authorized by the user, this credential allows the skill to access personal account-level data (such as private asset lists, sales history, and received offers)."
---

# Element NFT Market 🌊

Skill for querying NFT collection statistics, portfolios, and monitoring active trading events on the Element Market.

## 🚀 Setup

### Environment Variables
Ensure you have set the API Key in your environment or `.env` file:
```bash
export ELEMENT_API_KEY="your_api_key_here"

```

## 📊 Queries & Monitors

### Get Collection Stats

Use this to check the detailed volume, floor price, 24h average price, and the latest trade price for a specific NFT collection by its slug.

```bash
SLUG="boredapeyachtclub"
CHAIN="eth"

curl -s --request GET \
  --url "[https://api.element.market/openapi/v1/collection/stats?chain=$](https://api.element.market/openapi/v1/collection/stats?chain=$){CHAIN}&collection_slug=${SLUG}" \
  --header "X-Api-Key: ${ELEMENT_API_KEY}" \
  --header "accept: application/json" | jq '{volume24h: .data.stats1D.volume, saleCount24h: .data.stats1D.saleCount, floorPrice: .data.collectionFloorPrice.floorPriceSource, avgPrice24h: .data.stats1D.avgPrice, lastTradePrice: .data.lastTradePrice}'

```

### Get Ranking List

Use this to fetch the top trending NFT collections on a specific chain.

```bash
SORTTYPE="TOP"
CHAIN="eth"
LEVEL="L1D"
LIMIT="10"

curl -s --request GET \
     --url "[https://api.element.market/openapi/v1/collection/ranking?chain=$](https://api.element.market/openapi/v1/collection/ranking?chain=$){CHAIN}&sort_type=${SORTTYPE}&level=${LEVEL}&limit=${LIMIT}" \
     --header "X-Api-Key: ${ELEMENT_API_KEY}" \
     --header "accept: application/json" | jq '[.data.rankingList[].collectionRank | {name: .collection.name, slug: .collection.slug, floorPrice: .floorPrice, volume: .volume}]' 

```

### Get Wallet NFT Portfolio (Asset List)

Use this to get the list of NFTs owned by a specific wallet address.

* CHAIN can be "eth", "bsc", etc.
* WALLET_ADDRESS is the 0x address. ONLY leave this empty if the user explicitly asks to check their own personal wallet.
* LIMIT is the number of assets to return (default 10 to save tokens).

```bash
CHAIN="eth"
WALLET_ADDRESS="" 
LIMIT="10"

curl -s --request GET \
  --url "[https://api.element.market/openapi/v1/account/assetList?chain=$](https://api.element.market/openapi/v1/account/assetList?chain=$){CHAIN}&wallet_address=${WALLET_ADDRESS}&limit=${LIMIT}" \
  --header "X-Api-Key: ${ELEMENT_API_KEY}" \
  --header "accept: application/json" | jq '[.data.assetList[].asset | {name: .name, collection: .collection.name, tokenId: .tokenId, type: .tokenType, quantity: .ownedQuantity, image: .imagePreviewUrl}]'

```

### Get Received Offers (Offers on your NFTs)

Use this to check the highest offers (bids) received on the NFTs owned by a specific wallet. It automatically returns enriched data including floor price and last trade price.

* CHAIN can be "eth", "bsc", etc.
* WALLET_ADDRESS is the 0x address. ONLY leave this empty if the user explicitly asks to check their own personal wallet.
* 🚨 OUTPUT RULE: Render the `image` URL as a real https://www.google.com/search?q=image using Markdown: `![NFT Name](image_url)`. Below it, clearly show the Offer Price, Offerer, Floor Price, 24h Average Price, and Last Trade Price. Briefly point out if the offer is a good deal!

```bash
CHAIN="bsc"
WALLET_ADDRESS="" 
LIMIT="10"

curl -s --request GET \
  --url "[https://api.element.market/openapi/v1/account/offerReceived?chain=$](https://api.element.market/openapi/v1/account/offerReceived?chain=$){CHAIN}&wallet_address=${WALLET_ADDRESS}&limit=${LIMIT}" \
  --header "X-Api-Key: ${ELEMENT_API_KEY}" \
  --header "accept: application/json" | jq '[.data.assetList[] | select(.orderData.bestBid != null) | {name: .asset.name, collection: .asset.collection.name, slug: .asset.collection.slug, image: .asset.imagePreviewUrl, offerPrice: .orderData.bestBid.price, offerUSD: .orderData.bestBid.priceUSD, offerer: .orderData.bestBid.maker}]'

```

### Get Collection Slug by Contract Address (Address Resolver)

Use this tool when a user provides a smart contract address (e.g., 0x...) and you need to find the collection's `slug` to use in other queries. Automatically call `Get Collection Stats` using the resolved `slug` to provide comprehensive info.

```bash
CHAIN="bsc"
CONTRACT_ADDRESS="0xed5af388653567af2f388e6224dc7c4b3241c544"

curl -s --request GET \
  --url "[https://api.element.market/openapi/v1/contract?chain=$](https://api.element.market/openapi/v1/contract?chain=$){CHAIN}&contract_address=${CONTRACT_ADDRESS}" \
  --header "X-Api-Key: ${ELEMENT_API_KEY}" \
  --header "accept: application/json" | jq '{name: .data.collection.name, slug: .data.collection.slug, image: .data.collection.imageUrl}'

```

### Check Recent Wallet Sales Activity (All-in-One Monitor)

🔴 PRIMARY TRIGGER FOR PERSONAL TRANSACTIONS: You MUST use this tool whenever the user asks "Did I sell any NFTs recently?", "Check my recent sales", or when monitoring the wallet for new sales.
Use this to fetch the latest trading activities for a specific wallet, automatically resolving collection stats in the background.

* CHAIN can be "eth", "bsc", etc.
* WALLET_ADDRESS is the 0x address. ONLY leave this empty if the user explicitly asks to check their own personal wallet.
* LIMIT is the number of recent activities (default 5).
* 🚨 OUTPUT RULES (CRITICAL):
1. Action Logic: Compare `from` and `to` against `WALLET_ADDRESS` (or the default user). If `from` is the user, it is a "Sell". If `to` is the user, it is a "Buy".
2. Currency Logic: Dynamically determine the currency symbol based on the `CHAIN` parameter.
3. Formatting Template: You MUST output the final alert EXACTLY in this beautiful Markdown format for each transaction found:


🚨 **NFT Sale Monitor Alert!**
**Collection:** [collection]
**Token ID:** [tokenId]
💰 **Transaction Details:**
* **Action:** [Buy / Sell]
* **Price:** [salePrice] [Currency]
* **Counterparty:** `[from/to]`
* **Time:** [time]
* **Tx Receipt:** [https://[Chain_Scan_Domain]/tx/txHash]


📊 **Latest Collection Stats:**
* **Current Floor Price:** [floorPrice] [Currency]
* **24H Average Price:** [avgPrice24h] [Currency]
* **Last Trade Price:** [lastTradePrice] [Currency]


💡 **Agent Insight:** (Provide a 1-sentence analysis in English comparing the salePrice to the floorPrice/lastTradePrice.)

```bash
CHAIN="bsc"
WALLET_ADDRESS="" 
LIMIT="5"

ACTIVITIES=$(curl -s --request GET \
  --url "[https://api.element.market/openapi/v1/account/activity?chain=$](https://api.element.market/openapi/v1/account/activity?chain=$){CHAIN}&wallet_address=${WALLET_ADDRESS}&event_names=Sale&limit=${LIMIT}" \
  --header "X-Api-Key: ${ELEMENT_API_KEY}" \
  --header "accept: application/json" | jq -c '.data.activityList[].accountActivity | select(. != null)')

JSON_RESULT="["

while IFS= read -r activity; do
  if [ -z "$activity" ]; then continue; fi
  
  CONTRACT=$(echo "$activity" | jq -r '.contractAddress')
  TOKEN_ID=$(echo "$activity" | jq -r '.tokenId')
  PRICE_ETH=$(echo "$activity" | jq -r 'if .price != null then ((.price | tonumber) / 1000000000000000000) else 0 end')
  FROM_ADDR=$(echo "$activity" | jq -r '.fromAddress')
  TO_ADDR=$(echo "$activity" | jq -r '.toAddress')
  TIME=$(echo "$activity" | jq -r '.eventTime')
  TX_HASH=$(echo "$activity" | jq -r '.txHash')

  CONTRACT_RES=$(curl -s --request GET \
    --url "[https://api.element.market/openapi/v1/contract?chain=$](https://api.element.market/openapi/v1/contract?chain=$){CHAIN}&contract_address=${CONTRACT}" \
    --header "X-Api-Key: ${ELEMENT_API_KEY}" \
    --header "accept: application/json")
  
  COLLECTION_NAME=$(echo "$CONTRACT_RES" | jq -r '.data.collection.name // "Unknown"')
  SLUG=$(echo "$CONTRACT_RES" | jq -r '.data.collection.slug // empty')
  IMAGE_URL=$(echo "$CONTRACT_RES" | jq -r '.data.collection.imageUrl // ""')

  FLOOR_PRICE=0
  AVG_PRICE=0
  LAST_PRICE=0
  
  if [ -n "$SLUG" ] && [ "$SLUG" != "null" ]; then
    STATS_RES=$(curl -s --request GET \
      --url "[https://api.element.market/openapi/v1/collection/stats?chain=$](https://api.element.market/openapi/v1/collection/stats?chain=$){CHAIN}&collection_slug=${SLUG}" \
      --header "X-Api-Key: ${ELEMENT_API_KEY}" \
      --header "accept: application/json")
      
    FLOOR=$(echo "$STATS_RES" | jq -r '.data.collectionFloorPrice.floorPriceSource // empty')
    AVG=$(echo "$STATS_RES" | jq -r '.data.stats1D.avgPrice // empty')
    LAST=$(echo "$STATS_RES" | jq -r '.data.lastTradePrice // empty')
    
    [ -n "$FLOOR" ] && [ "$FLOOR" != "null" ] && FLOOR_PRICE=$FLOOR
    [ -n "$AVG" ] && [ "$AVG" != "null" ] && AVG_PRICE=$AVG
    [ -n "$LAST" ] && [ "$LAST" != "null" ] && LAST_PRICE=$LAST
  fi

  ITEM=$(jq -n \
    --arg name "$COLLECTION_NAME" \
    --arg image "$IMAGE_URL" \
    --arg tokenId "$TOKEN_ID" \
    --arg price "$PRICE_ETH" \
    --arg from "$FROM_ADDR" \
    --arg to "$TO_ADDR" \
    --arg time "$TIME" \
    --arg txHash "$TX_HASH" \
    --arg floor "$FLOOR_PRICE" \
    --arg avg "$AVG_PRICE" \
    --arg last "$LAST_PRICE" \
    '{collection: $name, tokenId: $tokenId, image: $image, salePrice: $price, from: $from, to: $to, time: $time, txHash: $txHash, floorPrice: $floor, avgPrice24h: $avg, lastTradePrice: $last}')
    
  JSON_RESULT="${JSON_RESULT}${ITEM},"
done <<< "$ACTIVITIES"

if [ "$JSON_RESULT" = "[" ]; then
  echo "[]"
else
  echo "${JSON_RESULT%?}]"
fi

```

### Check New Received Offers (Offer Monitor)

🔴 PRIMARY TRIGGER FOR OFFERS: You MUST use this tool whenever the user asks "Did I get any new offers?", "Monitor my new bids", or "Check for recent NFT offers".
Use this to fetch the most recent active offers received on the user's NFTs and automatically enrich them with real-time collection stats.

* CHAIN can be "eth", "bsc", etc.
* WALLET_ADDRESS is the 0x address. ONLY leave this empty if the user explicitly asks to check their own personal wallet.
* LIMIT is the number of offers to fetch (default 10).
* 🚨 OUTPUT RULES (CRITICAL):
1. Time Filtering: Check the `listingTime` of each offer. Compare it with the CURRENT TIME. ONLY display offers that were made recently. Ignore old offers.
2. Currency Logic: Dynamically determine the currency symbol based on the `CHAIN` parameter.
3. Formatting Template: You MUST output the final alert EXACTLY in this beautiful Markdown format for each new offer:


🔔 **New NFT Offer Alert!**
**Item:** [name]
**Collection:** [collection]
💰 **Offer Details:**
* **Offer Price:** [offerPrice] [Currency]
* **Offerer:** `[maker]`
* **Offer Time:** [listingTime]


📊 **Collection Stats (24H):**
* **Current Floor Price:** [floorPrice] [Currency]
* **24H Average Price:** [avgPrice24h] [Currency]
* **Last Trade Price:** [lastTradePrice] [Currency]
* **24H Sales Count:** [saleCount24h]


💡 **Agent Insight:** (Provide a brief 1-sentence analysis in English comparing the `offerPrice` to the `floorPrice` and `lastTradePrice`.)

```bash
CHAIN="bsc"
WALLET_ADDRESS="" 
LIMIT="10"

OFFERS=$(curl -s --request GET \
  --url "[https://api.element.market/openapi/v1/account/offerReceived?chain=$](https://api.element.market/openapi/v1/account/offerReceived?chain=$){CHAIN}&wallet_address=${WALLET_ADDRESS}&limit=${LIMIT}" \
  --header "X-Api-Key: ${ELEMENT_API_KEY}" \
  --header "accept: application/json" | jq -c '.data.assetList[] | select(.orderData.bestBid != null)')

JSON_RESULT="["

while IFS= read -r offer; do
  if [ -z "$offer" ]; then continue; fi
  
  NAME=$(echo "$offer" | jq -r '.asset.name // "Unknown"')
  COLLECTION_NAME=$(echo "$offer" | jq -r '.asset.collection.name // "Unknown"')
  SLUG=$(echo "$offer" | jq -r '.asset.collection.slug // empty')
  IMAGE_URL=$(echo "$offer" | jq -r '.asset.imagePreviewUrl // ""')
  PRICE=$(echo "$offer" | jq -r '.orderData.bestBid.price // 0')
  MAKER=$(echo "$offer" | jq -r '.orderData.bestBid.maker // "Unknown"')
  LISTING_TIME=$(echo "$offer" | jq -r '.orderData.bestBid.listingTime | todateiso8601')

  FLOOR_PRICE=0
  AVG_PRICE=0
  SALE_COUNT=0
  LAST_PRICE=0

  if [ -n "$SLUG" ] && [ "$SLUG" != "null" ]; then
    STATS_RES=$(curl -s --request GET \
      --url "[https://api.element.market/openapi/v1/collection/stats?chain=$](https://api.element.market/openapi/v1/collection/stats?chain=$){CHAIN}&collection_slug=${SLUG}" \
      --header "X-Api-Key: ${ELEMENT_API_KEY}" \
      --header "accept: application/json")
      
    FLOOR=$(echo "$STATS_RES" | jq -r '.data.collectionFloorPrice.floorPriceSource // empty')
    AVG=$(echo "$STATS_RES" | jq -r '.data.stats1D.avgPrice // empty')
    SALES=$(echo "$STATS_RES" | jq -r '.data.stats1D.saleCount // empty')
    LAST=$(echo "$STATS_RES" | jq -r '.data.lastTradePrice // empty')
    
    [ -n "$FLOOR" ] && [ "$FLOOR" != "null" ] && FLOOR_PRICE=$FLOOR
    [ -n "$AVG" ] && [ "$AVG" != "null" ] && AVG_PRICE=$AVG
    [ -n "$SALES" ] && [ "$SALES" != "null" ] && SALE_COUNT=$SALES
    [ -n "$LAST" ] && [ "$LAST" != "null" ] && LAST_PRICE=$LAST
  fi

  ITEM=$(jq -n \
    --arg name "$NAME" \
    --arg coll "$COLLECTION_NAME" \
    --arg img "$IMAGE_URL" \
    --arg price "$PRICE" \
    --arg maker "$MAKER" \
    --arg time "$LISTING_TIME" \
    --arg floor "$FLOOR_PRICE" \
    --arg avg "$AVG_PRICE" \
    --arg sales "$SALE_COUNT" \
    --arg last "$LAST_PRICE" \
    '{name: $name, collection: $coll, image: $img, offerPrice: $price, maker: $maker, listingTime: $time, floorPrice: $floor, avgPrice24h: $avg, saleCount24h: $sales, lastTradePrice: $last}')
    
  JSON_RESULT="${JSON_RESULT}${ITEM},"
done <<< "$OFFERS"

if [ "$JSON_RESULT" = "[" ]; then
  echo "[]"
else
  echo "${JSON_RESULT%?}]"
fi

```

## 🔗 Links

* [API Documentation](https://element.readme.io/reference/api-overview)
* [Create API Key](https://element.market/apikeys)
* [Mainnet](https://element.market)