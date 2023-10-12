#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   gen_share_token.py
@Time    :   2023/10/12 18:03:39
@Author  :   lvguanjun
@Desc    :   gen_share_token.py
"""

import requests

from custom_log import logger
from redis_cache import get_all_token
from config import SHARE_TOKEN_UNIQUE_NAME


def get_share_token(access_token):
    url = "https://ai.fakeopen.com/token/register"

    payload = {
        "unique_name": SHARE_TOKEN_UNIQUE_NAME,
        "access_token": access_token,
        "site_limit": "",
        "expires_in": 0,
        "show_conversations": False,
        "show_userinfo": True,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["token_key"]
    else:
        logger.error(
            f"get share token failed, {response.status_code=}, {response.text=}"
        )
        return None


def check_share_token(share_token):
    url = "https://ai.fakeopen.com/api/conversations"

    headers = {"Authorization": f"Bearer {share_token}"}

    response = requests.request("GET", url, headers=headers)

    if response.status_code == 200:
        return True
    if (
        response.status_code == 401
        and "Your OpenAI account has been deactivated" in response.text
    ):
        logger.error(f"account has been deactivated")
        return False
    logger.error(
        f"check share token exceptd, {response.status_code=}, {response.text=}"
    )
    return False


def main():
    share_tokens = []
    cur_count, err_count = 0, 0
    tokens = get_all_token()
    for access_token in tokens:
        share_token = get_share_token(access_token)
        if share_token:
            if check_share_token(share_token):
                share_tokens.append(share_token)
                cur_count += 1
            else:
                err_count += 1
    return cur_count, err_count, share_tokens


def gen_pool_token(share_tokens: list, pool_token: str = None):
    url = "https://ai.fakeopen.com/pool/update"

    payload = {
        "pool_token": pool_token,
        "share_tokens": "\n".join(share_tokens),
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()["pool_token"]
    else:
        logger.error(
            f"gen pool token failed, {response.status_code=}, {response.text=}"
        )
        return None


if __name__ == "__main__":
    cur_count, err_count, share_token = main()
    # pool_token = "pk-p3ggsOgldjpxxxx-_p9FnVULVbdBS1DRPV9xxxxxxxx"
    # pool_token = gen_pool_token(share_token, pool_token)
    # print(f"{cur_count=}, {err_count=}, {pool_token=}")
    print(f"{cur_count=}, {err_count=}, {share_token=}")
