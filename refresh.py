#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   refresh.py
@Time    :   2023/10/10 13:54:51
@Author  :   lvguanjun
@Desc    :   refresh.py
"""

import abc
import json
import time

import requests

from config import PROXY, REFRESH_EXTRA_TIME
from custom_log import logger
from redis_cache import get_need_refresh_tokens, set_to_redis


class TokenRefresher:
    def __init__(self, base_url, headers, payload):
        self.session = requests.Session()
        self.base_url = base_url
        self.headers = headers
        self.payload = payload

    @abc.abstractmethod
    def is_changed_password(self, response: requests.Response):
        pass

    def get_new_token(self, refresh_token):
        if PROXY:
            proxies = {"https": PROXY, "http": PROXY}
            self.session.proxies = proxies
        self.payload["refresh_token"] = refresh_token
        if self.headers["Content-Type"] == "application/json":
            payload = json.dumps(self.payload)
        else:
            payload = self.payload
        response = self.session.post(self.base_url, headers=self.headers, data=payload)
        if response.status_code == 200:
            update_token = response.json()
            update_token["refresh_token"] = refresh_token
            return update_token
        elif self.is_changed_password(response):
            return {"change_password": True}
        else:
            logger.error(f"{response.status_code=}, {response.text=}")
            return None

    def refresh_user_token(self, user, token):
        refresh_token = token["refresh_token"]
        update_token = self.get_new_token(refresh_token)
        if update_token is not None:
            if "refresh_token" not in update_token:
                token["change_password"] = True
                set_to_redis(user, token)
                logger.info(f"user change password, {user=}")
            else:
                set_to_redis(user, update_token)
                logger.info(f"refresh token success, {user=}")
        else:
            logger.error(f"refresh token failed, {user=}")

    def refresh_token(self, sleep_time: int):
        for user, token in get_need_refresh_tokens(REFRESH_EXTRA_TIME):
            self.refresh_user_token(user, token)
            time.sleep(sleep_time)


class Auth0TokenRefresher(TokenRefresher):
    def __init__(self):
        base_url = "https://auth0.openai.com/oauth/token"
        headers = {"Content-Type": "application/json"}
        payload = {
            "redirect_uri": (
                "com.openai.chat://auth0.openai.com/ios/com.openai.chat/callback"
            ),
            "grant_type": "refresh_token",
            "client_id": "pdlLIX2Y72MIl2rhLhTE9VV9bN905kBh",
        }
        super().__init__(base_url, headers, payload)

    def is_changed_password(self, response: requests.Response):
        return (
            response.status_code == 403
            and "Unknown or invalid refresh token." in response.text
        )


class FakeopenTokenRefresher(TokenRefresher):
    def __init__(self):
        base_url = "https://ai.fakeopen.com/auth/refresh"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {}
        super().__init__(base_url, headers, payload)

    def is_changed_password(self, response: requests.Response):
        """
        判断是否是因为修改密码导致的刷新失败
        ps: fakeopen的刷新接口返回太过简单，慎用来判断是否修改密码
        """
        return (
            response.status_code == 500
            and "error refresh access token" in response.text
        )


if __name__ == "__main__":
    auth0_token_refresher = Auth0TokenRefresher()
    fakeopen_token_refresher = FakeopenTokenRefresher()
    # auth0_token_refresher.refresh_token(1)
    fakeopen_token_refresher.refresh_token(0)
