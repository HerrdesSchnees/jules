import os
import time
import logging
from dotenv import load_dotenv
from worker.imap_client import IMAPClient
from worker.rspamd_client import RspamdClient
from worker.state_manager import StateManager

# Load environment variables
load_dotenv()

# Setup logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_path = os.getenv('LOG_PATH', 'logs/worker.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('imap-worker')

def process_mails():
    imap_host = os.getenv('IMAP_SERVER')
    imap_port = os.getenv('IMAP_PORT')
    imap_user = os.getenv('IMAP_USER')
    imap_pass = os.getenv('IMAP_PASSWORD')
    imap_ssl = os.getenv('IMAP_USE_SSL', 'True').lower() == 'true'

    rspamd_url = os.getenv('RSPAMD_URL')
    rspamd_pass = os.getenv('RSPAMD_PASSWORD')

    db_path = os.getenv('DATABASE_PATH')

    state_manager = StateManager(db_path)
    rspamd_client = RspamdClient(rspamd_url, rspamd_pass)
    imap_client = IMAPClient(imap_host, imap_port, imap_user, imap_pass, imap_ssl)

    try:
        imap_client.connect()
        imap_client.select_mailbox(os.getenv('IMAP_MAILBOX', 'INBOX'))

        msg_ids = imap_client.get_unseen_messages()
        logger.info(f"Found {len(msg_ids)} unseen messages")

        for mid in msg_ids:
            message_id_header = imap_client.get_message_id(mid)

            if state_manager.is_processed(message_id_header):
                logger.debug(f"Message {message_id_header} already processed, skipping.")
                continue

            raw_mail = imap_client.fetch_message(mid)
            if not raw_mail:
                logger.warning(f"Could not fetch message {mid}")
                continue

            result = rspamd_client.check_mail(raw_mail)
            if result:
                score = result.get('score')
                action = result.get('action')
                symbols = result.get('symbols', {})

                logger.info(f"Message {message_id_header} - Score: {score}, Action: {action}")

                state_manager.mark_processed(message_id_header, score, action)
                # Here you could implement further actions based on the Rspamd result
                # e.g., move to junk folder, add headers, etc.
            else:
                logger.error(f"Failed to check message {message_id_header} with Rspamd")

    except Exception as e:
        logger.exception(f"Error in main loop: {e}")
    finally:
        try:
            imap_client.logout()
        except:
            pass

if __name__ == "__main__":
    logger.info("Starting IMAP Worker Phase 1 (Simulation)")
    while True:
        process_mails()
        # In simulation mode, we might want a short sleep or long sleep
        time.sleep(30)
