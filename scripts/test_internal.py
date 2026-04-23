import unittest
from unittest.mock import MagicMock, patch
import os
import sqlite3
from worker.state_manager import StateManager
from worker.rspamd_client import RspamdClient
from worker.imap_client import IMAPClient

class TestWorkerComponents(unittest.TestCase):
    def setUp(self):
        self.db_path = 'data/state/test_state.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.state_manager = StateManager(self.db_path)

    def test_state_manager(self):
        msg_id = "<test@example.com>"
        self.assertFalse(self.state_manager.is_processed(msg_id))
        self.state_manager.mark_processed(msg_id, 5.0, "add header")
        self.assertTrue(self.state_manager.is_processed(msg_id))

        # Verify persistence
        new_sm = StateManager(self.db_path)
        self.assertTrue(new_sm.is_processed(msg_id))

    @patch('requests.post')
    def test_rspamd_client(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'score': 10, 'action': 'reject'}

        client = RspamdClient("http://localhost:11333/checkv2", "password")
        result = client.check_mail(b"Subject: Test")

        self.assertEqual(result['score'], 10)
        self.assertEqual(result['action'], 'reject')
        mock_post.assert_called_once()

    def test_imap_client_mock(self):
        # We can't easily test imaplib without a server, so we mock the connection
        client = IMAPClient("localhost", 143, "user", "pass", False)
        client.connection = MagicMock()

        client.connection.search.return_value = ('OK', [b'1 2'])
        ids = client.get_unseen_messages()
        self.assertEqual(ids, [b'1', b'2'])

        client.connection.fetch.return_value = ('OK', [(None, b'Message-ID: <id1>')])
        mid = client.get_message_id(b'1')
        self.assertEqual(mid, '<id1>')

if __name__ == '__main__':
    unittest.main()
