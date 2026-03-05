#!/usr/bin/env python3
"""
ONE-TIME YouTube OAuth Setup
=============================
Run this ONCE in Google Cloud Shell (browser-based, no local install needed).
It generates a token you paste into GitHub Secrets — then everything is automatic forever.

Instructions:
  1. Go to shell.cloud.google.com (free, no install)
  2. Upload this file
  3. Run: pip install google-auth-oauthlib google-api-python-client && python setup_youtube.py
  4. A URL appears — open it in browser → log in with your-email@gmail.com → Allow
  5. Paste the code back → token printed → paste into GitHub Secrets
"""
import json
import sys

CLIENT_SECRETS = {
    "installed": {
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

def main():
    print("=" * 60)
    print("AutoTuber — YouTube OAuth Setup")
    print("=" * 60)

    client_id     = input("\nPaste your YouTube CLIENT ID: ").strip()
    client_secret = input("Paste your YouTube CLIENT SECRET: ").strip()

    secrets = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }

    with open("client_secrets.json", "w") as f:
        json.dump(secrets, f)

    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)

    print("\n➡  A URL will appear below.")
    print("   Open it in your browser → log in with your-email@gmail.com → click Allow")
    print("   Then paste the code here.\n")

    creds = flow.run_console()

    token_json = creds.to_json()
    client_secrets_json = json.dumps(secrets)

    print("\n" + "=" * 60)
    print("✅ SUCCESS! Add these 4 secrets to GitHub:")
    print("=" * 60)
    print("\n1. Secret name: YOUTUBE_TOKEN_JSON")
    print("   Value:")
    print(token_json)
    print("\n2. Secret name: YOUTUBE_CLIENT_SECRETS")
    print("   Value:")
    print(client_secrets_json)
    print("\n3. Secret name: YOUTUBE_CLIENT_ID")
    print("   Value:", client_id)
    print("\n4. Secret name: YOUTUBE_CLIENT_SECRET")
    print("   Value:", client_secret)
    print("\n5. Secret name: ANTHROPIC_API_KEY")
    print("   Value: REDACTED_ANTHROPIC_KEY")
    print("\n6. Secret name: PEXELS_API_KEY")
    print("   Value: REDACTED_PEXELS_KEY")
    print("\n" + "=" * 60)
    print("After adding secrets → pipeline runs automatically. Done forever.")
    print("=" * 60)

if __name__ == "__main__":
    main()
