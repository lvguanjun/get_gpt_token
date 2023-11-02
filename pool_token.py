#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   pool_token.py
@Time    :   2023/10/23 16:33:01
@Author  :   lvguanjun
@Desc    :   pool_token.py
"""

import datetime
import json

import requests

from config import DATETIME_FORMAT, POOL_TOKEN
from custom_log import logger
from redis_cache import redis_cli


def get_active_token(extra_time: int = 0) -> list:
    """
    获取所有幸存的的share_token
    """
    survive_tokens = []
    for user in redis_cli.keys("*==*"):
        token = redis_cli.get(user)
        token = json.loads(token)
        expire_time = token["expired_time"]
        expire_time = datetime.datetime.strptime(expire_time, DATETIME_FORMAT)
        if (
            datetime.datetime.now() + datetime.timedelta(seconds=extra_time)
            > expire_time
        ):
            continue
        if all(
            [
                not token.get("deactivated"),
            ]
        ):
            survive_tokens.append(token["share_token"])
    return survive_tokens


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
    share_tokens = get_active_token()
    pool_token = gen_pool_token(share_tokens, POOL_TOKEN)
    print(pool_token)
