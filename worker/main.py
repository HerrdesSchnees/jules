#!/usr/bin/env python3
"""
Jules IMAP Worker - Simulation/Real Mode
Reads mails from IMAP, sends to Rspamd for analysis, and logs decisions.
"""

import email
import hashlib
import imaplib
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import requests

# Config
MODE = os.getenv("JULES_MODE", "simulation")
IMAP_SERVER = os.getenv("IMAP_SERVER", "jules-dovecot")
IMAP_PORT = int(os.getenv("IMAP_PORT", "143"))
IMAP_USER = os.getenv("IMAP_USER", "vagrant")
IMAP_PASS = os.getenv("IMAP_PASS", "vagrant")
IMAP_SSL = os.getenv("IMAP_SSL", "false").lower() == "true"
IMAP_MAILBOX = os.getenv("IMAP_MAILBOX", "INBOX")
JUNK_MAILBOX = os.getenv("JUNK_MAILBOX", "Junk")
RSPAMD_URL = os.getenv("RSPAMD_URL", "http://jules-rspamd:11334")
RSPAMD_PASSWORD = os.getenv("RSPAMD_PASSWORD", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

# Paths
LOG_DIR = Path("/app/logs")
STATE_DIR = Path("/app/state")
LOG_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)

# Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "worker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("jules")

# State DB
STATE_DB = STATE_DIR / "state.db"


def init_state() -> None:
    conn = sqlite3.connect(str(STATE_DB))
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS processed (
            msg_id TEXT PRIMARY KEY,
            source_uid TEXT,
            subject TEXT,
            score REAL,
            action TEXT,
            is_spam INTEGER,
            processed_at TEXT
        )'''
    )
    conn.commit()
    conn.close()
    logger.info("State DB initialized")


def is_processed(message_key: str) -> bool:
    conn = sqlite3.connect(str(STATE_DB))
    c = conn.cursor()
    c.execute("SELECT 1 FROM processed WHERE msg_id = ?", (message_key,))
    result = c.fetchone() is not None
    conn.close()
    return result


def mark_processed(message_key: str, source_uid: str, subject: str, score: float, action: str, is_spam: bool) -> None:
    conn = sqlite3.connect(str(STATE_DB))
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO processed VALUES (?, ?, ?, ?, ?, ?, ?)",
        (message_key, source_uid, subject, score, action, int(is_spam), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def analyze_with_rspamd(raw_mail: bytes) -> dict:
    """Send raw mail to Rspamd controller and return parsed response."""
    try:
        headers = {"Content-Type": "message/rfc822"}
        if RSPAMD_PASSWORD:
            headers["Password"] = RSPAMD_PASSWORD

        resp = requests.post(
            f"{RSPAMD_URL}/checkv2",
            data=raw_mail,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Rspamd request failed: {e}")
        return {}


def get_message_key(msg) -> str:
    """Prefer Message-ID, otherwise derive a stable fallback key."""
    message_id = (msg.get("Message-ID") or "").strip()
    if message_id:
        return message_id

    digest_src = "|".join(
        [
            msg.get("Date", ""),
            msg.get("From", ""),
            msg.get("To", ""),
            msg.get("Subject", ""),
        ]
    )
    digest = hashlib.sha256(digest_src.encode("utf-8", errors="ignore")).hexdigest()
    return f"fallback-{digest}"


def should_treat_as_spam(result: dict, score: float, required: float) -> bool:
    action = (result.get("action") or "").lower()
    spam_actions = {"reject", "add header", "rewrite subject", "soft reject"}
    return action in spam_actions or score >= required


def open_imap_connection():
    if IMAP_SSL:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    else:
        mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
    mail.login(IMAP_USER, IMAP_PASS)
    return mail


def process_mailbox() -> None:
    logger.info(
        "Starting worker in %s mode (dry_run=%s, mailbox=%s, server=%s:%s)",
        MODE,
        DRY_RUN,
        IMAP_MAILBOX,
        IMAP_SERVER,
        IMAP_PORT,
    )

    try:
        mail = open_imap_connection()
        mail.select(IMAP_MAILBOX)
        logger.info("Connected to IMAP %s:%s", IMAP_SERVER, IMAP_PORT)

        _, data = mail.search(None, "ALL")
        msg_ids = data[0].split()
        logger.info("Found %d messages", len(msg_ids))

        for msg_uid in msg_ids:
            uid_text = msg_uid.decode()

            _, msg_data = mail.fetch(msg_uid, "(RFC822)")
            if not msg_data or not msg_data[0]:
                logger.warning("Could not fetch message UID %s", uid_text)
                continue

            raw_mail = msg_data[0][1]
            msg = email.message_from_bytes(raw_mail)
            subject = msg.get("Subject", "(no subject)")
            message_key = get_message_key(msg)

            if is_processed(message_key):
                logger.debug("Skipping already processed: %s", message_key)
                continue

            result = analyze_with_rspamd(raw_mail)
            if not result:
                logger.warning("No Rspamd result for %s", message_key)
                continue

            score = float(result.get("score", 0.0))
            required = float(result.get("required_score", 6.0))
            action = result.get("action", "unknown")
            symbols = list(result.get("symbols", {}).keys())
            is_spam = should_treat_as_spam(result, score, required)

            logger.info(
                "Mail: %s | Key: %s | Score: %.2f/%.2f | Action: %s | Spam: %s | Symbols: %s",
                subject[:60],
                message_key,
                score,
                required,
                action,
                is_spam,
                symbols[:5],
            )

            mark_processed(message_key, uid_text, subject, score, action, is_spam)

            if DRY_RUN:
                logger.info("[DRY-RUN] Would %s", "move to spam" if is_spam else "keep in inbox")
            elif is_spam:
                mail.copy(msg_uid, JUNK_MAILBOX)
                mail.store(msg_uid, "+FLAGS", "\\Deleted")
                logger.info("Moved to %s: %s", JUNK_MAILBOX, message_key)

        mail.close()
        mail.logout()
        logger.info("Worker cycle complete")

    except Exception as e:
        logger.error(f"Worker error: {e}", exc_info=True)


def main() -> None:
    init_state()
    process_mailbox()
    logger.info("Worker finished")


if __name__ == "__main__":
    main()
