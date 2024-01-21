#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   gen_share_token.py
@Time    :   2023/10/12 18:03:39
@Author  :   lvguanjun
@Desc    :   gen_share_token.py
"""

import requests

from config import BASE_URL, POOL_TOKEN, SHARE_TOKEN_UNIQUE_NAME
from custom_log import logger

from concurrent.futures import ThreadPoolExecutor
from redis_cache import get_all_token, set_to_redis


def get_share_token(token):
    if share_token := token.get("share_token"):
        return share_token

    url = BASE_URL + "/api/token/register"

    payload = {
        "unique_name": SHARE_TOKEN_UNIQUE_NAME,
        "access_token": token["access_token"],
        "site_limit": "",
        "expires_in": 0,
        "show_conversations": True,
        "show_userinfo": True,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
    except Exception as e:
        logger.error(f"get share token exceptd, {e=}")
        return None

    if response.status_code == 200:
        share_token = response.json()["token_key"]
        token["share_token"] = share_token
        set_to_redis(token["user"], token)
        return share_token
    else:
        logger.error(
            f"get share token failed, {response.status_code=}, {response.text=}"
        )
        return None


def check_share_token(share_token):
    url = BASE_URL + "/backend-api/models"

    headers = {"Authorization": f"Bearer {share_token}"}

    try:
        response = requests.request("GET", url, headers=headers)
    except Exception as e:
        logger.error(f"check share token exceptd, {e=}")
        return False

    if response.status_code == 200:
        return True
    if response.status_code == 401 and any(
        [
            "Your OpenAI account has been deactivated" in response.text,
            "Your authentication token has expired." in response.text,
        ]
    ):
        logger.error(f"account has been deactivated or token has expired")
        return False
    logger.error(
        f"check share token exceptd, {response.status_code=}, {response.text=}"
    )
    return False


def get_user_name(share_token) -> str:
    url = BASE_URL + "/backend-api/me"

    headers = {"Authorization": f"Bearer {share_token}"}

    try:
        response = requests.request("GET", url, headers=headers)
    except Exception as e:
        logger.error(f"get user name exceptd, {e=}")
        return None

    if response.status_code == 200:
        return response.json()["name"]
    logger.error(f"get user name failed, {response.status_code=}, {response.text=}")
    return None


def worker(token, check_all: bool = False):
    share_token = get_share_token(token)
    if not share_token:
        return
    if not check_all and token.get("deactivated"):
        return
    if check_share_token(share_token):
        if check_all and token.pop("deactivated", None):
            set_to_redis(token["user"], token)
        logger.info(f"{share_token} is valid")
    else:
        logger.error(f"get share token failed, {token['user']=}")
        token["deactivated"] = True
        set_to_redis(token["user"], token)


def main(check_all: bool = False):
    tokens = get_all_token()
    with ThreadPoolExecutor(max_workers=10) as executor:
        for token in tokens:
            executor.submit(worker, token, check_all)
    logger.info("All tasks are completed.")


def gen_pool_token(share_tokens: list, pool_token: str = None):
    url = BASE_URL + "/api/pool/update"

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
    # cur_count, err_count, share_token = main()
    # # pool_token = gen_pool_token(share_token, POOL_TOKEN)
    # # print(f"{cur_count=}, {err_count=}, {pool_token=}")
    # print(f"{cur_count=}, {err_count=}, {share_token=}")
    main()