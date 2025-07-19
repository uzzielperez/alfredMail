"""
Gmail API Setup Script
Run this once to authenticate and generate credentials.json
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def setup_gmail_auth():
    """Set up Gmail API authentication"""
    creds = None
    
    # Check if we already have credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # You need to download credentials.json from Google Cloud Console first
            if not os.path.exists('client_credentials.json'):
                print("❌ Missing client_credentials.json!")
                print("\n📋 To get this file:")
                print("1. Go to: https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable Gmail API")
                print("4. Go to Credentials → Create Credentials → OAuth client ID")
                print("5. Choose 'Desktop application'")
                print("6. Download the JSON file and rename it to 'client_credentials.json'")
                print("7. Put it in this folder and run this script again")
                return False
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        # Also save as credentials.json for your app
        with open('credentials.json', 'w') as f:
            f.write(creds.to_json())
    
    print("✅ Gmail API authentication successful!")
    return True

if __name__ == "__main__":
    print("🔧 Setting up Gmail API authentication...")
    success = setup_gmail_auth()
    
    if success:
        print("\n🎉 Setup complete! You can now run your Streamlit app.")
        print("Run: streamlit run streamlit_app.py")
    else:
        print("\n💡 Please get your client_credentials.json file first.") 