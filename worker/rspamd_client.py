import requests
import logging

class RspamdClient:
    def __init__(self, url, password=None):
        self.url = url
        self.headers = {}
        if password:
            self.headers['Password'] = password

    def check_mail(self, raw_mail):
        try:
            response = requests.post(
                self.url,
                data=raw_mail,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error communicating with Rspamd: {e}")
            return None
