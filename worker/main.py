#!/usr/bin/env python3
"""
Jules IMAP Worker - Simulation Mode
Reads mails from IMAP, sends to Rspamd for analysis, logs decisions.
"""

import imaplib
import email
import requests
import json
import sqlite3
import os
import logging
import time
from datetime import datetime
from pathlib import Path

# Config
MODE = os.getenv("JULES_MODE", "simulation")
IMAP_SERVER = os.getenv("IMAP_SERVER", "jules-dovecot")
IMAP_PORT = int(os.getenv("IMAP_PORT", "143"))
IMAP_USER = os.getenv("IMAP_USER", "vagrant")
IMAP_PASS = os.getenv("IMAP_PASS", "vagrant")
RSPAMD_URL = os.getenv("RSPAMD_URL", "http://jules-rspamd:11334")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

# Paths
LOG_DIR = Path("/app/logs")
STATE_DIR = Path("/app/state")
LOG_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)

# Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "worker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("jules")

# State DB
STATE_DB = STATE_DIR / "state.db"

def init_state():
    conn = sqlite3.connect(str(STATE_DB))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS processed (
        msg_id TEXT PRIMARY KEY,
        subject TEXT,
        score REAL,
        action TEXT,
        is_spam INTEGER,
        processed_at TEXT
    )''')
    conn.commit()
    conn.close()
    logger.info("State DB initialized")

def is_processed(msg_id: str) -> bool:
    conn = sqlite3.connect(str(STATE_DB))
    c = conn.cursor()
    c.execute("SELECT 1 FROM processed WHERE msg_id = ?", (msg_id,))
    result = c.fetchone() is not None
    conn.close()
    return result

def mark_processed(msg_id: str, subject: str, score: float, action: str, is_spam: bool):
    conn = sqlite3.connect(str(STATE_DB))
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO processed VALUES (?, ?, ?, ?, ?, ?)",
        (msg_id, subject, score, action, int(is_spam), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def analyze_with_rspamd(raw_mail: bytes) -> dict:
    """Send raw mail to Rspamd and return parsed response."""
    try:
        resp = requests.post(
            f"{RSPAMD_URL}/checkv2",
            data=raw_mail,
            headers={"Content-Type": "message/rfc822"},
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Rspamd request failed: {e}")
        return {}

def process_mailbox():
    logger.info(f"Starting worker in {MODE} mode (dry_run={DRY_RUN})")
    
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
        mail.login(IMAP_USER, IMAP_PASS)
        mail.select("inbox")
        logger.info(f"Connected to IMAP {IMAP_SERVER}:{IMAP_PORT}")
        
        # Search for all messages
        _, data = mail.search(None, "ALL")
        msg_ids = data[0].split()
        logger.info(f"Found {len(msg_ids)} messages")
        
        for msg_id in msg_ids:
            msg_id_str = msg_id.decode()
            
            if is_processed(msg_id_str):
                logger.debug(f"Skipping already processed: {msg_id_str}")
                continue
            
            # Fetch raw mail
            _, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_mail = msg_data[0][1]
            
            # Parse for subject
            msg = email.message_from_bytes(raw_mail)
            subject = msg.get("Subject", "(no subject)")
            
            # Analyze with Rspamd
            result = analyze_with_rspamd(raw_mail)
            
            if not result:
                logger.warning(f"No Rspamd result for {msg_id_str}")
                continue
            
            score = result.get("score", 0.0)
            required = result.get("required_score", 6.0)
            action = result.get("action", "unknown")
            symbols = list(result.get("symbols", {}).keys())
            
            is_spam = score >= required
            
            logger.info(
                f"Mail: {subject[:60]} | Score: {score:.2f}/{required:.2f} | "
                f"Action: {action} | Spam: {is_spam} | Symbols: {symbols[:5]}"
            )
            
            # Record state
            mark_processed(msg_id_str, subject, score, action, is_spam)
            
            if DRY_RUN:
                logger.info(f"[DRY-RUN] Would {'move to spam' if is_spam else 'keep in inbox'}")
            else:
                if is_spam:
                    # Move to spam folder (real mode)
                    mail.copy(msg_id, "Junk")
                    mail.store(msg_id, "+FLAGS", "\\Deleted")
                    logger.info(f"Moved to Junk: {msg_id_str}")
        
        mail.close()
        mail.logout()
        logger.info("Worker cycle complete")
        
    except Exception as e:
        logger.error(f"Worker error: {e}", exc_info=True)

def main():
    init_state()
    process_mailbox()
    logger.info("Worker finished")

if __name__ == "__main__":
    main()
