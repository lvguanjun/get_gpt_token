#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   refresh.py
@Time    :   2023/10/10 13:54:51
@Author  :   lvguanjun
@Desc    :   refresh.py
"""

import requests

from config import PROXY, REFRESH_EXTRA_TIME
from custom_log import logger
from redis_cache import get_need_refresh_tokens, set_to_redis


def refresh_token():
    base_url = "https://auth0.openai.com/oauth/token"
    headers = {"Content-Type": "application/json"}
    payload = {
        "redirect_uri": (
            "com.openai.chat://auth0.openai.com/ios/com.openai.chat/callback"
        ),
        "grant_type": "refresh_token",
        "client_id": "pdlLIX2Y72MIl2rhLhTE9VV9bN905kBh",
    }
    session = requests.Session()
    if PROXY:
        proxies = {"https": PROXY, "http": PROXY}
        session.proxies = proxies
    for user, token in get_need_refresh_tokens(REFRESH_EXTRA_TIME):
        refresh_token = token["refresh_token"]
        payload["refresh_token"] = refresh_token
        response = session.post(base_url, headers=headers, json=payload)
        if response.status_code == 200:
            update_token = response.json()
            # 新获取的 token 不携带 refresh_token ，因此需要手动添加
            update_token["refresh_token"] = refresh_token
            set_to_redis(user, update_token)
            logger.info(f"refresh token success, {user=}")
        elif (
            response.status_code == 403
            and "Unknown or invalid refresh token." in response.text
        ):
            token["change_password"] = True
            set_to_redis(user, token)
            logger.info(f"user change password, {user=}")
        else:
            logger.error(f"{user=}, {response.status_code=}, {response.text=}")
            continue


if __name__ == "__main__":
    refresh_token()
