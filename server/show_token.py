#!/usr/bin/env python3
"""
Utility script to show or reset the authentication token.
Run this when you need to copy the token for the UI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from auth import _generate_token, _hash_token, init_auth

TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".meshwork_token")

def show_current():
    """Show the current token (requires resetting to see plaintext)."""
    print("Token is stored hashed. To see plaintext, use --reset.")
    print(f"Token file: {TOKEN_FILE}")
    if os.path.exists(TOKEN_FILE):
        print("Token file exists. Use --reset to generate a new one and display it.")
    else:
        print("No token file exists. Use --reset to generate one.")

def reset_token():
    """Reset and display a new token."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print("Removed old token file.")
    
    # Generate new token
    token = _generate_token()
    hashed = _hash_token(token)
    
    with open(TOKEN_FILE, "w") as f:
        f.write(hashed)
    
    print("\n" + "="*60)
    print("  YOUR NEW ACCESS TOKEN (copy this exactly):")
    print(f"  {token}")
    print("="*60 + "\n")
    print("Paste this token into the Controls tab authentication form.")
    print("It will be stored in your browser localStorage.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_token()
    else:
        show_current()
