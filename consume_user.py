#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   consume_user.py
@Time    :   2023/10/09 20:03:35
@Author  :   lvguanjun
@Desc    :   consume_user.py
"""

# -*- coding: utf-8 -*-


import time
from collections import deque

import requests

from config import BASE_URL, LOGIN_URL
from custom_log import logger
from redis_cache import (
    get_from_redis,
    gpt3_redis_cli,
    is_in_error_set,
    set_error_to_redis,
    set_to_gpt3_redis,
    set_to_redis,
)


class AccountInvalidException(Exception):
    pass


def get_token(user_name, password) -> dict:
    url = LOGIN_URL
    payload = {
        "username": user_name,
        "password": password,
    }
    headeds = {"content-type": "application/x-www-form-urlencoded"}
    response = requests.request("POST", url, data=payload, headers=headeds)
    if response.status_code == 200:
        return response.json()
    if response.status_code == 500 and any(
        [
            "wrong email or password" in response.text,
            "it has been deleted or deactivated" in response.text,
            "wrong username or password" in response.text,
        ]
    ):
        raise AccountInvalidException
    raise Exception(f"{response.status_code=}, {response.text=}")


def check_is_gpt4(token):
    url = BASE_URL + "/backend-api/models"

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            categories = response.json()["categories"]
            for category in categories:
                if category["category"] == "gpt_4":
                    return True
            return False
        raise Exception(f"{response.status_code=}, {response.text=}")
    except Exception as e:
        raise Exception(f"{e=}")


def consume_user(q: deque, sleep_time: int = 0, max_consume: int = 0):
    size = 0
    while True:
        if max_consume and size >= max_consume:
            return
        user = q.pop()
        if user is None:
            break
        user_name, password = user
        if is_in_error_set(f"{user_name}=={password}"):
            logger.info(f"{user_name} in error set")
            continue
        if get_from_redis(f"{user_name}=={password}") is not None:
            logger.info(f"{user_name} already in redis")
            continue
        if get_from_redis(f"{user_name}=={password}", gpt3_redis_cli) is not None:
            logger.info(f"{user_name} already in gpt3 redis")
            continue
        size += 1
        try:
            res: dict = get_token(user_name, password)
            if not check_is_gpt4(res["access_token"]):
                set_to_gpt3_redis(f"{user_name}=={password}", res)
                set_error_to_redis(f"{user_name}=={password}")
                logger.info(f"{user_name} not gpt4")
                time.sleep(sleep_time)
                continue
            set_to_redis(f"{user_name}=={password}", res)
            logger.info(f"{user_name} add to redis")
        except AccountInvalidException:
            set_error_to_redis(f"{user_name}=={password}")
            logger.info(f"account invalid: {user_name}")
        except Exception as e:
            logger.error(f"{user_name=}, {password=}, {e=}")
        time.sleep(sleep_time)


if __name__ == "__main__":
    pass
