#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   refresh.py
@Time    :   2023/10/10 13:54:51
@Author  :   lvguanjun
@Desc    :   refresh.py
"""

import time

import requests

from config import PROXY, REFRESH_EXTRA_TIME
from custom_log import logger
from redis_cache import get_need_refresh_tokens, set_to_redis


def get_new_token(refresh_token, session: requests.Session):
    base_url = "https://auth0.openai.com/oauth/token"
    headers = {"Content-Type": "application/json"}
    payload = {
        "redirect_uri": (
            "com.openai.chat://auth0.openai.com/ios/com.openai.chat/callback"
        ),
        "grant_type": "refresh_token",
        "client_id": "pdlLIX2Y72MIl2rhLhTE9VV9bN905kBh",
        "refresh_token": refresh_token,
    }
    if PROXY:
        proxies = {"https": PROXY, "http": PROXY}
        session.proxies = proxies
    response = session.post(base_url, headers=headers, json=payload)
    if response.status_code == 200:
        update_token = response.json()
        # 新获取的 token 不携带 refresh_token ，因此需要手动添加
        update_token["refresh_token"] = refresh_token
        return update_token
    elif (
        response.status_code == 403
        and "Unknown or invalid refresh token." in response.text
    ):
        return {"change_password": True}
    else:
        logger.error(f"{response.status_code=}, {response.text=}")
        return None


def refresh_user_token(user, token, session: requests.Session):
    refresh_token = token["refresh_token"]
    update_token = get_new_token(refresh_token, session)
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


def refresh_token(session: requests.Session, sleep_time: int):
    for user, token in get_need_refresh_tokens(REFRESH_EXTRA_TIME):
        refresh_user_token(user, token, session)
        time.sleep(sleep_time)


if __name__ == "__main__":
    sleep_time = 1
    session = requests.Session()
    refresh_token(session, sleep_time)
