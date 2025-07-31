import requests

import utils


class User:
    def __init__(self, mid: int | None = -1) -> None:
        self.mid = mid
        self.refresh_token = ''
        self.name = ''
        self.last_cookies_update = -1
        self.session: requests.Session = utils.setup_session()
        self.logined = 0
        self.added = 0
    
    def __str__(self):
        return f"User(mid={self.mid}, name={self.name}, logined={self.logined})"

users = {}