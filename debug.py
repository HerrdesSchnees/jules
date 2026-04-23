#!/usr/bin/env python3
"""Debug script for Jules IMAP Worker"""

import os
import sys
import requests
import sqlite3
from pathlib import Path

RSPAMD_URL = os.getenv("RSPAMD_URL", "http://jules-rspamd:11334")

def check_config():
    print("[1/5] Checking configuration files...")
    files = ["docker-compose.yaml", "Dockerfile.worker", "requirements.txt", ".env.example"]
    for f in files:
        if Path(f).exists():
            print(f"  ✓ {f}")
        else:
            print(f"  ✗ {f} MISSING")
    print()

def check_rspamd():
    print("[2/5] Checking Rspamd availability...")
    try:
        resp = requests.get(f"{RSPAMD_URL}/ping", timeout=5)
        if resp.status_code == 200:
            print(f"  ✓ Rspamd reachable at {RSPAMD_URL}")
        else:
            print(f"  ✗ Rspamd returned status {resp.status_code}")
    except Exception as e:
        print(f"  ✗ Rspamd unreachable: {e}")
    print()

def check_worker():
    print("[3/5] Checking worker config...")
    if Path("worker/main.py").exists():
        print("  ✓ worker/main.py found")
    else:
        print("  ✗ worker/main.py missing")
    print()

def check_testmails():
    print("[4/5] Checking test mails...")
    maildir = Path("testdata/mail")
    if maildir.exists():
        mails = list(maildir.glob("*.txt"))
        print(f"  ✓ {len(mails)} test mails found")
        for m in mails:
            print(f"    - {m.name}")
    else:
        print("  ✗ testdata/mail missing")
    print()

def check_state():
    print("[5/5] Checking state persistence...")
    db = Path("state/state.db")
    if db.exists():
        print(f"  ✓ State DB exists ({db.stat().st_size} bytes)")
        conn = sqlite3.connect(str(db))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM processed")
        count = c.fetchone()[0]
        print(f"  ✓ {count} messages processed")
        conn.close()
    else:
        print("  ℹ State DB not yet created (will be created on first run)")
    print()

def main():
    print("=" * 50)
    print("Jules IMAP Worker - Debug Check")
    print("=" * 50)
    print()
    
    check_config()
    check_rspamd()
    check_worker()
    check_testmails()
    check_state()
    
    print("Debug check complete.")

if __name__ == "__main__":
    main()
