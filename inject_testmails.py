#!/usr/bin/env python3
"""Inject test mails into Dovecot Maildir"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

MAILDIR = Path("/var/mail/vagrant/Maildir")
TESTDATA = Path("/app/testdata/mail")

def ensure_maildir():
    for subdir in ["cur", "new", "tmp"]:
        (MAILDIR / subdir).mkdir(parents=True, exist_ok=True)

def inject_mails():
    ensure_maildir()
    
    if not TESTDATA.exists():
        print(f"Testdata not found at {TESTDATA}")
        return
    
    for mailfile in sorted(TESTDATA.glob("*.txt")):
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique = f"{timestamp}.{os.getpid()}.{mailfile.stem}"
        target = MAILDIR / "new" / unique
        
        shutil.copy(mailfile, target)
        print(f"Injected: {mailfile.name} -> {target.name}")
    
    print(f"Done. Check {MAILDIR}/new/")

if __name__ == "__main__":
    inject_mails()
