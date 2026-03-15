#!/usr/bin/env python3
"""
Google Ads API Authentication Script
Handles OAuth flow and stores refresh token for API access.
"""

import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# OAuth scopes for Google Ads API
SCOPES = ['https://www.googleapis.com/auth/adwords']

def main():
    # Load client credentials
    client_secrets_file = os.path.expanduser('~/.openclaw/credentials/gog-oauth-google-ads.json')
    
    if not os.path.exists(client_secrets_file):
        print(f"Error: {client_secrets_file} not found")
        print("Make sure OAuth credentials are set up in Google Cloud Console")
        sys.exit(1)
    
    # Run OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES)
    
    # Use console flow (no browser needed on remote)
    credentials = flow.run_console()
    
    # Store refresh token
    refresh_token = credentials.refresh_token
    
    print(f"\nRefresh token: {refresh_token}")
    print("\nAdd this to your credentials or environment:")
    print(f"GOOGLE_ADS_REFRESH_TOKEN={refresh_token}")
    
    # Save to file for reference
    token_file = os.path.expanduser('~/.openclaw/credentials/google-ads-refresh-token.txt')
    with open(token_file, 'w') as f:
        f.write(refresh_token)
    
    print(f"\nToken saved to: {token_file}")
    print("Add to load-keys.sh: export GOOGLE_ADS_REFRESH_TOKEN=$(cat ~/.openclaw/credentials/google-ads-refresh-token.txt)")

if __name__ == '__main__':
    main()
