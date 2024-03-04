from typing import Union

import requests
import tls_client

from lib.common.utils import JsonFileB


class CookieExt:
    cookie: JsonFileB

    def __init__(self, cookie: str):
        self.cookie = JsonFileB(cookie)

    def new_cookie(self, session: Union[requests.Response, tls_client.Session]):
        b = {}
        for c in session.cookies:
            if c.name == "session_token":
                continue
            b.update({
                c.name: c.value
            })
        self.cookie.dumpdict(b)

    def read_cookie(self):
        b = []
        cookie_values = self.cookie.read().j
        for g in cookie_values:
            b.append(f"{g}={cookie_values[g]}")
        cookie_values = ";".join(b)
        print(cookie_values)
        return cookie_values

    def patch_cookie(self, session: Union[requests.Response, tls_client.Session]):
        b = self.cookie.read().j
        print(session.cookies)
        if isinstance(session, tls_client.Session):
            for c in session.cookies:
                b.update({
                    c.name: c.value
                })
        if isinstance(session, requests.Response):
            lngsession = dict(session.cookies)
            b.update(lngsession)

        self.cookie.dumpdict(b)

    def has(self, key: str):
        return True if key in self.cookie.read().j else False

    def get(self, key: str):
        b = self.cookie.read().j
        return b.get(key)
