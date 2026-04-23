import os
import sys
import requests
import imaplib
from dotenv import load_dotenv

# Add parent directory to path to allow importing from worker
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worker.imap_client import IMAPClient
from worker.rspamd_client import RspamdClient

load_dotenv()

def debug():
    print("--- Starting Debug Check ---")

    # 1. Check Config
    print("Checking configuration...")
    required_vars = ['IMAP_SERVER', 'IMAP_USER', 'IMAP_PASSWORD', 'RSPAMD_URL']
    for var in required_vars:
        val = os.getenv(var)
        print(f"  {var}: {'OK' if val else 'MISSING'}")

    # 2. Check Rspamd Connectivity
    print("\nChecking Rspamd connectivity...")
    rspamd_url = os.getenv('RSPAMD_URL')
    try:
        # Try a simple ping or GET to the base URL
        base_url = rspamd_url.rsplit('/', 1)[0]
        resp = requests.get(base_url, timeout=5)
        print(f"  Rspamd status: {resp.status_code}")
    except Exception as e:
        print(f"  Rspamd unreachable: {e}")

    # 3. Check IMAP Connectivity
    print("\nChecking IMAP connectivity...")
    try:
        host = os.getenv('IMAP_SERVER')
        port = os.getenv('IMAP_PORT')
        user = os.getenv('IMAP_USER')
        password = os.getenv('IMAP_PASSWORD')
        ssl = os.getenv('IMAP_USE_SSL', 'True').lower() == 'true'

        client = IMAPClient(host, port, user, password, ssl)
        client.connect()
        print("  IMAP Connection: OK")
        client.logout()
    except Exception as e:
        print(f"  IMAP Connection failed: {e}")

    print("\n--- Debug Check Finished ---")

if __name__ == "__main__":
    debug()
