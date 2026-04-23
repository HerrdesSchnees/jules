import imaplib
import logging

class IMAPClient:
    def __init__(self, host, port, user, password, use_ssl=True):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.use_ssl = use_ssl
        self.connection = None

    def connect(self):
        if self.use_ssl:
            self.connection = imaplib.IMAP4_SSL(self.host, self.port)
        else:
            self.connection = imaplib.IMAP4(self.host, self.port)
        self.connection.login(self.user, self.password)
        logging.info(f"Connected to IMAP server {self.host}:{self.port}")

    def select_mailbox(self, mailbox='INBOX'):
        self.connection.select(mailbox)

    def get_unseen_messages(self):
        status, messages = self.connection.search(None, 'UNSEEN')
        if status != 'OK':
            return []
        return messages[0].split()

    def fetch_message(self, msg_id):
        status, data = self.connection.fetch(msg_id, '(RFC822)')
        if status != 'OK':
            return None
        return data[0][1]

    def get_message_id(self, msg_id):
        # Fetch Message-ID header specifically for state management
        status, data = self.connection.fetch(msg_id, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
        if status != 'OK':
            return None
        header = data[0][1].decode('utf-8', errors='ignore')
        for line in header.splitlines():
            if line.lower().startswith('message-id:'):
                return line.split(':', 1)[1].strip()

        # Fallback to UID if available, otherwise sequence number
        status, uid_data = self.connection.fetch(msg_id, '(UID)')
        if status == 'OK':
            # Example response: [b'1 (UID 123)']
            uid_str = uid_data[0].decode('utf-8', errors='ignore')
            if 'UID' in uid_str:
                return f"internal-uid-{uid_str.split('UID')[1].strip(' )')}"

        return f"internal-id-{msg_id.decode()}"

    def logout(self):
        if self.connection:
            self.connection.logout()
