import argparse
import sys
import json
import os
import requests

BASE_URL = "https://pro-api.solscan.io/v2.0"

def get_api_key():
    api_key = os.environ.get("SOLSCAN_API_KEY")
    if not api_key:
        print("Error: SOLSCAN_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    return api_key

def make_request(endpoint, params=None):
    api_key = get_api_key()
    headers = {
        "token": api_key,
        "User-Agent": "Agent-Skill/1.0"
    }
    url = f"{BASE_URL}{endpoint}"
    # Remove None values
    if params:
        params = {k: v for k, v in params.items() if v is not None}
        
    try:
        response = requests.get(url, headers={
                                                "token": api_key,
                                                "User-Agent": "Agent-Skill/1.0"
                                            }, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response Body: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def print_result(data):
    print(json.dumps(data, indent=2))

# --- Account Commands ---
def setup_account_parser(subparsers):
    parser = subparsers.add_parser('account', help='Account operations')
    sp = parser.add_subparsers(dest='action', required=True)

    sp.add_parser('detail', help='Get account details').add_argument('--address', required=True)
    sp.add_parser('data-decoded', help='Get decoded data').add_argument('--address', required=True)
    
    p_tokens = sp.add_parser('tokens', help='Get token accounts')
    p_tokens.add_argument('--address', required=True)
    p_tokens.add_argument('--page', type=int, default=1)
    p_tokens.add_argument('--page-size', type=int, default=10)

    p_txs = sp.add_parser('transactions', help='Get transactions')
    p_txs.add_argument('--address', required=True)
    p_txs.add_argument('--page', type=int, default=1)
    p_txs.add_argument('--page-size', type=int, default=10)
    
    p_transfers = sp.add_parser('transfers', help='Get transfers')
    p_transfers.add_argument('--address', required=True)
    p_transfers.add_argument('--page', type=int, default=1)
    p_transfers.add_argument('--page-size', type=int, default=10)

    sp.add_parser('stake', help='Get stake accounts').add_argument('--address', required=True)
    sp.add_parser('portfolio', help='Get portfolio').add_argument('--address', required=True)
    
    p_defi = sp.add_parser('defi', help='Get DeFi activities')
    p_defi.add_argument('--address', required=True)
    p_defi.add_argument('--page', type=int, default=1)
    p_defi.add_argument('--page-size', type=int, default=10)

    sp.add_parser('defi-export', help='Export DeFi activities').add_argument('--address', required=True)

    p_balance = sp.add_parser('balance-change', help='Get balance changes')
    p_balance.add_argument('--address', required=True)
    p_balance.add_argument('--page', type=int, default=1)
    p_balance.add_argument('--page-size', type=int, default=10)

    sp.add_parser('reward-export', help='Export rewards').add_argument('--address', required=True)
    sp.add_parser('transfer-export', help='Export transfers').add_argument('--address', required=True)
    
    sp.add_parser('metadata', help='Get metadata').add_argument('--address', required=True)
    sp.add_parser('metadata-multi', help='Get multiple metadata').add_argument('--addresses', required=True, help='Comma separated addresses')

    p_leader = sp.add_parser('leaderboard', help='Get leaderboard')
    p_leader.add_argument('--page', type=int, default=1)
    p_leader.add_argument('--page-size', type=int, default=10)

def handle_account(args):
    if args.action == 'detail': return make_request("/account/detail", {"address": args.address})
    elif args.action == 'data-decoded': return make_request("/account/data-decoded", {"address": args.address})
    elif args.action == 'tokens': return make_request("/account/token-accounts", {"address": args.address, "page": args.page, "page_size": args.page_size})
    elif args.action == 'transactions': return make_request("/account/transactions", {"address": args.address, "page": args.page, "page_size": args.page_size})
    elif args.action == 'transfers': return make_request("/account/transfer", {"address": args.address, "page": args.page, "page_size": args.page_size})
    elif args.action == 'stake': return make_request("/account/stake", {"address": args.address})
    elif args.action == 'portfolio': return make_request("/account/portfolio", {"address": args.address})
    elif args.action == 'defi': return make_request("/account/defi/activities", {"address": args.address, "page": args.page, "page_size": args.page_size})
    elif args.action == 'defi-export': return make_request("/account/defi/activities/export", {"address": args.address})
    elif args.action == 'balance-change': return make_request("/account/balance_change", {"address": args.address, "page": args.page, "page_size": args.page_size})
    elif args.action == 'reward-export': return make_request("/account/reward/export", {"address": args.address})
    elif args.action == 'transfer-export': return make_request("/account/transfer/export", {"address": args.address})
    elif args.action == 'metadata': return make_request("/account/metadata", {"address": args.address})
    elif args.action == 'metadata-multi': return make_request("/account/metadata/multi", {"address": args.addresses})
    elif args.action == 'leaderboard': return make_request("/account/leaderboard", {"page": args.page, "page_size": args.page_size})

# --- Token Commands ---
def setup_token_parser(subparsers):
    parser = subparsers.add_parser('token', help='Token operations')
    sp = parser.add_subparsers(dest='action', required=True)

    sp.add_parser('meta', help='Get metadata').add_argument('--address', required=True)
    sp.add_parser('meta-multi', help='Get multiple metadata').add_argument('--addresses', required=True)
    
    p_holders = sp.add_parser('holders', help='Get holders')
    p_holders.add_argument('--address', required=True)
    p_holders.add_argument('--page', type=int, default=1)
    p_holders.add_argument('--page-size', type=int, default=10)
    
    sp.add_parser('price', help='Get price').add_argument('--address', required=True)
    sp.add_parser('price-multi', help='Get multiple prices').add_argument('--addresses', required=True)

    p_market = sp.add_parser('markets', help='Get markets')
    p_market.add_argument('--address', required=True)
    p_market.add_argument('--page', type=int, default=1)
    
    sp.add_parser('trending', help='Get trending').add_argument('--limit', type=int, default=10)

    p_list = sp.add_parser('list', help='List tokens')
    p_list.add_argument('--page', type=int, default=1)
    p_list.add_argument('--page-size', type=int, default=10)
    p_list.add_argument('--sort_by', default='market_cap_rank')
    p_list.add_argument('--direction', default='asc')

    sp.add_parser('top', help='Get top tokens').add_argument('--filter', default='all')
    sp.add_parser('latest', help='Get latest tokens').add_argument('--limit', type=int, default=10)
    
    p_transfer = sp.add_parser('transfers', help='Get token transfers')
    p_transfer.add_argument('--address', required=True)
    p_transfer.add_argument('--page', type=int, default=1)
    p_transfer.add_argument('--page-size', type=int, default=10)

    p_defi = sp.add_parser('defi', help='Get DeFi activities')
    p_defi.add_argument('--address', required=True)
    p_defi.add_argument('--page', type=int, default=1)
    p_defi.add_argument('--page-size', type=int, default=10)
    
    sp.add_parser('defi-export', help='Export DeFi activities').add_argument('--address', required=True)
    
    p_hist = sp.add_parser('historical', help='Get historical data')
    p_hist.add_argument('--address', required=True)
    p_hist.add_argument('--type', default='line')
    p_hist.add_argument('--time_from', type=int)
    p_hist.add_argument('--time_to', type=int)

    sp.add_parser('search', help='Search tokens').add_argument('--query', required=True)

def handle_token(args):
    if args.action == 'meta': return make_request("/token/meta", {"address": args.address})
    elif args.action == 'meta-multi': return make_request("/token/meta/multi", {"address": args.addresses})
    elif args.action == 'holders': return make_request("/token/holders", {"address": args.address, "page": args.page, "page_size": args.page_size})
    elif args.action == 'price': return make_request("/token/price", {"address": args.address})
    elif args.action == 'price-multi': return make_request("/token/price/multi", {"address": args.addresses})
    elif args.action == 'markets': return make_request("/token/markets", {"address": args.address, "page": args.page})
    elif args.action == 'trending': return make_request("/token/trending", {"limit": args.limit})
    elif args.action == 'list': return make_request("/token/list", {"page": args.page, "page_size": args.page_size, "sort_by": args.sort_by, "direction": args.direction})
    elif args.action == 'top': return make_request("/token/top", {"filter": args.filter})
    elif args.action == 'latest': return make_request("/token/latest", {"limit": args.limit})
    elif args.action == 'transfers': return make_request("/token/transfer", {"address": args.address, "page": args.page, "page_size": args.page_size})
    elif args.action == 'defi': return make_request("/token/defi/activities", {"address": args.address, "page": args.page, "page_size": args.page_size})
    elif args.action == 'defi-export': return make_request("/token/defi/activities/export", {"address": args.address})
    elif args.action == 'historical': return make_request("/token/historical-data", {"address": args.address, "type": args.type, "time_from": args.time_from, "time_to": args.time_to})
    elif args.action == 'search': return make_request("/token/search", {"q": args.query})


# --- Transaction Commands ---
def setup_transaction_parser(subparsers):
    parser = subparsers.add_parser('transaction', help='Transaction operations')
    sp = parser.add_subparsers(dest='action', required=True)

    sp.add_parser('detail', help='Get details').add_argument('--signature', required=True)
    sp.add_parser('detail-multi', help='Get multiple details').add_argument('--signatures', required=True, help='Comma separated keys')
    sp.add_parser('last', help='Get last transactions').add_argument('--limit', type=int, default=10)
    
    p_actions = sp.add_parser('actions', help='Get actions')
    p_actions.add_argument('--signature', required=True)

    p_actions_m = sp.add_parser('actions-multi', help='Get multiple actions')
    p_actions_m.add_argument('--signatures', required=True)
    
    sp.add_parser('fees', help='Get fees').add_argument('--signature', required=True)

def handle_transaction(args):
    if args.action == 'detail': return make_request("/transaction/detail", {"tx": args.signature})
    elif args.action == 'detail-multi': return make_request("/transaction/detail/multi", {"txs": args.signatures})
    elif args.action == 'last': return make_request("/transaction/last", {"limit": args.limit})
    elif args.action == 'actions': return make_request("/transaction/actions", {"tx": args.signature})
    elif args.action == 'actions-multi': return make_request("/transaction/actions/multi", {"txs": args.signatures})
    elif args.action == 'fees': return make_request("/transaction/fees", {"tx": args.signature})


# --- NFT Commands ---
def setup_nft_parser(subparsers):
    parser = subparsers.add_parser('nft', help='NFT operations')
    sp = parser.add_subparsers(dest='action', required=True)
    
    sp.add_parser('news', help='Get news')
    
    p_act = sp.add_parser('activities', help='Get activities')
    p_act.add_argument('--address', required=True)
    p_act.add_argument('--page', type=int, default=1)
    
    p_cols = sp.add_parser('collections', help='Get collections')
    p_cols.add_argument('--page', type=int, default=1)
    p_cols.add_argument('--page-size', type=int, default=10)
    
    p_items = sp.add_parser('items', help='Get collection items')
    p_items.add_argument('--address', required=True)
    p_items.add_argument('--page', type=int, default=1)
    p_items.add_argument('--page-size', type=int, default=10)

def handle_nft(args):
    if args.action == 'news': return make_request("/nft/news")
    elif args.action == 'activities': return make_request("/nft/activities", {"token_address": args.address, "page": args.page})
    elif args.action == 'collections': return make_request("/nft/collection/lists", {"page": args.page, "page_size": args.page_size})
    elif args.action == 'items': return make_request("/nft/collection/items", {"collection": args.address, "page": args.page, "page_size": args.page_size})


# --- Block Commands ---
def setup_block_parser(subparsers):
    parser = subparsers.add_parser('block', help='Block operations')
    sp = parser.add_subparsers(dest='action', required=True)
    
    p_last = sp.add_parser('last', help='Get last blocks')
    p_last.add_argument('--limit', type=int, default=10, help='Limit (10, 20, 30, 40, 60, 100)')
    
    sp.add_parser('detail', help='Get block detail').add_argument('--block', required=True)
    
    p_txs = sp.add_parser('transactions', help='Get block transactions')
    p_txs.add_argument('--block', required=True)
    p_txs.add_argument('--page', type=int, default=1)
    p_txs.add_argument('--page-size', type=int, default=10)

def handle_block(args):
    if args.action == 'last': return make_request("/block/last", {"limit": args.limit})
    elif args.action == 'detail': return make_request("/block/detail", {"block": args.block})
    elif args.action == 'transactions': return make_request("/block/transactions", {"block": args.block, "page": args.page, "page_size": args.page_size})


# --- Market Commands ---
def setup_market_parser(subparsers):
    parser = subparsers.add_parser('market', help='Market operations')
    sp = parser.add_subparsers(dest='action', required=True)
    
    sp.add_parser('list', help='List markets')
    sp.add_parser('info', help='Market info')
    sp.add_parser('volume', help='Market volume')

def handle_market(args):
    if args.action == 'list': return make_request("/market/list")
    elif args.action == 'info': return make_request("/market/info")
    elif args.action == 'volume': return make_request("/market/volume")

# --- Program Commands ---
def setup_program_parser(subparsers):
    parser = subparsers.add_parser('program', help='Program operations')
    sp = parser.add_subparsers(dest='action', required=True)
    
    p_list = sp.add_parser('list', help='List programs')
    p_list.add_argument('--page', type=int, default=1)
    p_list.add_argument('--page-size', type=int, default=10)
    p_list.add_argument('--sort_by', default='tx_count_24h')
    p_list.add_argument('--direction', default='desc')
    
    sp.add_parser('popular', help='Popular platforms')
    
    p_analytics = sp.add_parser('analytics', help='Program analytics')
    p_analytics.add_argument('--address', required=True)
    p_analytics.add_argument('--type', default='24h')

def handle_program(args):
    if args.action == 'list': return make_request("/program/list", {"page": args.page, "page_size": args.page_size, "sort_by": args.sort_by, "direction": args.direction})
    elif args.action == 'popular': return make_request("/program/popular/platforms")
    elif args.action == 'analytics': return make_request("/program/analytics", {"program_address": args.address, "type": args.type})

# --- Monitor Commands ---
def setup_monitor_parser(subparsers):
    parser = subparsers.add_parser('monitor', help='Monitor operations')
    sp = parser.add_subparsers(dest='action', required=True)
    
    sp.add_parser('usage', help='Get API usage')

def handle_monitor(args):
    if args.action == 'usage': return make_request("/monitor/usage")

def main():
    parser = argparse.ArgumentParser(description="Solscan Pro CLI Tool")
    subparsers = parser.add_subparsers(dest='resource', required=True)

    setup_account_parser(subparsers)
    setup_token_parser(subparsers)
    setup_transaction_parser(subparsers)
    setup_nft_parser(subparsers)
    setup_block_parser(subparsers)
    setup_market_parser(subparsers)
    setup_program_parser(subparsers)
    setup_monitor_parser(subparsers)

    args = parser.parse_args()

    data = {}
    if args.resource == 'account': data = handle_account(args)
    elif args.resource == 'token': data = handle_token(args)
    elif args.resource == 'transaction': data = handle_transaction(args)
    elif args.resource == 'nft': data = handle_nft(args)
    elif args.resource == 'block': data = handle_block(args)
    elif args.resource == 'market': data = handle_market(args)
    elif args.resource == 'program': data = handle_program(args)
    elif args.resource == 'monitor': data = handle_monitor(args)

    print_result(data)

if __name__ == "__main__":
    main()
