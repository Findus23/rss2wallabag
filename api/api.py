import hashlib
from datetime import datetime
from typing import Dict, List

from requests import Session


class WallabagAPI:
    def __init__(self, host: str,
                 user_agent="RSS2Wallabag +https://github.com/Findus23/rss2wallabag",
                 requests_session: Session = None
                 ) -> None:

        self.host = host
        self.token = None
        self.user_agent = user_agent
        if requests_session:
            self.s = requests_session
        else:
            self.s = Session()
        self.s.headers.update({"User-Agent": user_agent})

    def auth(self, client_id: str, client_secret: str, username: str, password: str) -> None:
        r = self.s.post(self.host + "/oauth/v2/token", data={
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password
        })
        r.raise_for_status()
        self.token = r.json()["access_token"]

    def check_auth(self):
        if not self.token:
            raise RuntimeError("call auth() first to log in")

    @property
    def auth_headers(self) -> Dict[str, str]:
        self.check_auth()
        return {"Authorization": "Bearer " + self.token}

    def add_entry(self, url: str, title: str = None,
                  tags: List[str] = None, published: datetime = None) -> None:
        if tags is None:
            tags = []

        data = {
            "url": url,
        }
        if title:
            data["title"] = title
        if tags:
            data["tags"] = ",".join(tags)
        if published:
            data["published_at"] = published.timestamp()
            # TODO: doesn't seem to be working
        r = self.s.post(self.host + "/api/entries.json", data=data, headers=self.auth_headers)
        r.raise_for_status()

    def check_exist(self, url: str) -> bool:
        sha1 = hashlib.sha1(url.encode()).hexdigest()
        r = self.s.get(self.host + "/api/entries/exists.json", params={
            "hashed_url": sha1,
        }, headers=self.auth_headers)
        r.raise_for_status()
        return r.json()["exists"]
