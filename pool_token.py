#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   pool_token.py
@Time    :   2023/10/23 16:33:01
@Author  :   lvguanjun
@Desc    :   pool_token.py
"""

import asyncio
import datetime
import json

import aiohttp
import requests

from config import BASE_URL, DATETIME_FORMAT, POOL_TOKEN
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


async def check_chat(session, token) -> bool:
    url = BASE_URL + "/v1/chat/completions"

    rate_sleep_time = 5  # 触发限速后，sleep 5s

    payload = {
        "messages": [
            {"role": "user", "content": "hi"},
        ],
        "model": "gpt-4-32k",
        "temperature": 1,
        "presence_penalty": 0,
        "top_p": 1,
        "frequency_penalty": 0,
        "stream": False,
        "max_tokens": 1,
    }
    headers = {"Authorization": f"Bearer {token}"}

    async with session.post(url, headers=headers, json=payload) as response:
        print(response.status)
        if response.status == 429 and await response.json() == {
            "detail": "rate limited."
        }:
            print(f"rate limited, and sleep {rate_sleep_time}s")
            await asyncio.sleep(rate_sleep_time)
            return await check_chat(session, token)
        if response.status not in [200, 429]:
            print(await response.json())
            return False
        return response.status == 200


# 异步函数来处理限速逻辑
async def process_tokens(share_tokens):
    sleep_time = 3.5  # 3/10s

    async with aiohttp.ClientSession() as session:
        effective_tokens = []
        for token in share_tokens:
            res = await asyncio.gather(
                check_chat(session, token), asyncio.sleep(sleep_time)
            )
            if res[0]:
                effective_tokens.append(token)
    return effective_tokens


def gen_pool_token(share_tokens: list, pool_token: str = None):
    url = BASE_URL + "/pool/update"

    payload = {
        "pool_token": pool_token,
        "share_tokens": "\n".join(share_tokens),
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        print(data)
        return data["pool_token"]
    else:
        logger.error(
            f"gen pool token failed, {response.status_code=}, {response.text=}"
        )
        return None


async def main():
    effective_file = "effective_tokens.txt"
    append_file = "append.txt"
    share_tokens = get_active_token()
    effective_tokens = await process_tokens(share_tokens)
    with open(effective_file, "w") as f:
        json.dump(effective_tokens, f)
    with open(append_file, "a") as f:
        f.write("\n")
        f.write("\n".join(effective_tokens))
    pool_token = gen_pool_token(effective_tokens, POOL_TOKEN)
    print(pool_token)


if __name__ == "__main__":
    asyncio.run(main())
