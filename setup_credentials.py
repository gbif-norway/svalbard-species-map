#!/usr/bin/env python3
"""
GBIF Credentials Setup Helper

This script helps users set up their GBIF credentials for the download API.
"""

import os
import getpass
from pathlib import Path

def setup_credentials():
    """Interactive setup for GBIF credentials."""
    print("🔐 GBIF Credentials Setup")
    print("=" * 50)
    print()
    print("To use the GBIF download API and get a DOI, you need a GBIF account.")
    print("If you don't have one, create a free account at: https://www.gbif.org/")
    print()
    
    # Get credentials
    email = input("Enter your GBIF email address: ").strip()
    password = getpass.getpass("Enter your GBIF password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required!")
        return False
    
    # Validate email format
    if '@' not in email:
        print("❌ Please enter a valid email address!")
        return False
    
    print()
    print("📝 Setting up credentials...")
    
    # Create .env file
    env_content = f"""# GBIF Credentials
# This file contains your GBIF account credentials
# Keep this file secure and don't commit it to version control

GBIF_USERNAME={email}
GBIF_PASSWORD={password}
"""
    
    env_file = Path(".env")
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    # Update .gitignore if needed
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        with open(gitignore_file, 'w') as f:
            f.write(".env\n")
    else:
        with open(gitignore_file, 'r') as f:
            content = f.read()
        if ".env" not in content:
            with open(gitignore_file, 'a') as f:
                f.write("\n.env\n")
    
    print("✅ Credentials saved to .env file")
    print("✅ .env file added to .gitignore for security")
    print()
    print("🔧 Next steps:")
    print("1. The pipeline will automatically use these credentials")
    print("2. You can also set environment variables manually:")
    print(f"   export GBIF_USERNAME='{email}'")
    print("   export GBIF_PASSWORD='your_password'")
    print()
    print("🚀 Ready to run the download pipeline!")
    print("   python download_gbif_data.py")
    print("   or")
    print("   docker-compose up --build")
    
    return True

def check_existing_credentials():
    """Check if credentials are already configured."""
    # Check .env file
    if Path(".env").exists():
        print("✅ Found .env file with credentials")
        return True
    
    # Check environment variables
    if os.getenv('GBIF_USERNAME') and os.getenv('GBIF_PASSWORD'):
        print("✅ Found GBIF credentials in environment variables")
        return True
    
    # Check gbif_config.py
    try:
        from gbif_config import GBIF_USERNAME, GBIF_PASSWORD
        if (GBIF_USERNAME != 'your_email@example.com' and 
            GBIF_PASSWORD != 'your_password'):
            print("✅ Found GBIF credentials in gbif_config.py")
            return True
    except ImportError:
        pass
    
    return False

def main():
    """Main function."""
    print("🔍 Checking for existing GBIF credentials...")
    
    if check_existing_credentials():
        print()
        print("✅ Credentials are already configured!")
        print("You can run the download pipeline now.")
        return True
    
    print()
    print("❌ No GBIF credentials found.")
    print()
    
    response = input("Would you like to set up credentials now? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        return setup_credentials()
    else:
        print("📝 You can set up credentials later by:")
        print("1. Creating a .env file with GBIF_USERNAME and GBIF_PASSWORD")
        print("2. Setting environment variables")
        print("3. Updating gbif_config.py")
        print("4. Running this script again")
        return False

if __name__ == "__main__":
    main() 