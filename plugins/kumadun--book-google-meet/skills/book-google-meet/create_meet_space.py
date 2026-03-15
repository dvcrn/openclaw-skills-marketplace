#!/usr/bin/env python3
"""Create a Google Meet space with AccessType.OPEN using Meet API v2."""

import os
import sys
import json
import pickle
import argparse
import urllib.request
import urllib.error
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Meet API v2 scopes
SCOPES = ['https://www.googleapis.com/auth/meetings.space.created']

def get_client_config():
    """Load client config from gog's stored credentials."""
    # Support custom credentials path via environment variable
    creds_path = os.environ.get('GOG_CREDENTIALS_PATH')
    
    if not creds_path:
        # Default path based on platform
        if os.name == 'nt':  # Windows
            creds_path = os.path.expanduser('~/AppData/Roaming/gogcli/credentials.json')
        else:  # macOS/Linux
            creds_path = os.path.expanduser('~/.config/gogcli/credentials.json')
    
    if not os.path.exists(creds_path):
        raise FileNotFoundError(
            f"Credentials file not found: {creds_path}\n"
            f"Please run: gog auth credentials /path/to/client_secret.json\n"
            f"Or set GOG_CREDENTIALS_PATH environment variable to your credentials file."
        )
    
    with open(creds_path, 'r') as f:
        creds = json.load(f)
    
    return {
        "installed": {
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }

def get_credentials():
    """Get valid user credentials from storage."""
    creds = None
    token_path = 'meet_token.pickle'
    
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = get_client_config()
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def create_meet_space_with_open_access():
    """Create a Meet space with AccessType.OPEN using Meet API v2."""
    creds = get_credentials()
    if not creds:
        print("Failed to get credentials")
        return
    
    # Get access token
    access_token = creds.token
    
    # Create space with OPEN access type and auto-recording/transcription
    space_body = {
        "config": {
            "accessType": "OPEN",
            "entryPointAccess": "ALL",
            "artifactConfig": {
                "recordingConfig": {
                    "autoRecordingGeneration": "ON"
                },
                "transcriptionConfig": {
                    "autoTranscriptionGeneration": "ON"
                }
            }
        }
    }
    
    # Make direct API call to Meet API v2
    url = 'https://meet.googleapis.com/v2/spaces'
    
    req = urllib.request.Request(
        url,
        data=json.dumps(space_body).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            space = json.loads(response.read().decode('utf-8'))
            print("✅ Meet space created successfully!")
            print(f"\n📅 Space Name: {space.get('name')}")
            print(f"🔗 Meeting URI: {space.get('meetingUri')}")
            print(f"🎥 Meeting Code: {space.get('meetingCode')}")
            
            if 'config' in space:
                config = space['config']
                print(f"🔓 Access Type: {config.get('accessType', 'N/A')}")
                print(f"🚪 Entry Point Access: {config.get('entryPointAccess', 'N/A')}")
                
                if 'artifactConfig' in config:
                    artifact_config = config['artifactConfig']
                    if 'recordingConfig' in artifact_config:
                        print(f"📹 Auto Recording: {artifact_config['recordingConfig'].get('autoRecordingGeneration', 'N/A')}")
                    if 'transcriptionConfig' in artifact_config:
                        print(f"📝 Auto Transcription: {artifact_config['transcriptionConfig'].get('autoTranscriptionGeneration', 'N/A')}")
            
            print(f"\n📋 Full Response:")
            print(json.dumps(space, indent=2))
            
            return space
    except urllib.error.HTTPError as e:
        print(f"❌ Error creating space: {e.code}")
        error_body = e.read().decode('utf-8')
        print(error_body)
        
        # Try to parse error
        try:
            error_json = json.loads(error_body)
            if 'error' in error_json:
                print(f"\nError details: {error_json['error'].get('message', 'Unknown error')}")
                print(f"Status: {error_json['error'].get('status', 'Unknown')}")
        except:
            pass
        
        return None

def main():
    parser = argparse.ArgumentParser(
        description='Create a Google Meet space with custom access settings.'
    )
    parser.add_argument(
        '--credentials',
        '-c',
        help='Path to gog credentials file (overrides GOG_CREDENTIALS_PATH env var)'
    )
    parser.add_argument(
        '--access-type',
        '-a',
        choices=['OPEN', 'TRUSTED', 'RESTRICTED'],
        default='OPEN',
        help='Meeting access type (default: OPEN)'
    )
    parser.add_argument(
        '--no-recording',
        action='store_true',
        help='Disable auto-recording'
    )
    parser.add_argument(
        '--no-transcription',
        action='store_true',
        help='Disable auto-transcription'
    )
    
    args = parser.parse_args()
    
    # Set credentials path from CLI arg if provided
    if args.credentials:
        os.environ['GOG_CREDENTIALS_PATH'] = args.credentials
    
    create_meet_space_with_open_access()

if __name__ == '__main__':
    main()
