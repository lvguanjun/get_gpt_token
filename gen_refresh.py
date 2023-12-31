#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   gen_refresh.py
@Time    :   2023/12/22 17:58:45
@Author  :   lvguanjun
@Desc    :   gen_refresh.py
"""

import datetime
import json

import requests

from config import BASE_URL, DATETIME_FORMAT, LOGIN_URL
from custom_log import logger
from redis_cache import redis_cli, update_and_add_to_redis


def get_need_refresh_user() -> list:
    """
    获取存活但未有refresh_token的user
    """
    users = []
    for user in redis_cli.keys("*==*"):
        token = redis_cli.get(user)
        token = json.loads(token)
        expire_time = token["expired_time"]
        expire_time = datetime.datetime.strptime(expire_time, DATETIME_FORMAT)
        if datetime.datetime.now() > expire_time:
            continue
        if redis_cli.sismember("error-user", user):
            print(f"{user=} in error set")
            continue
        if all(
            [
                not token.get("change_password"),
                not token.get("deactivated"),
                not token.get("refresh_token"),
            ]
        ):
            users.append(user)
    return users


def get_refresh_token(user):
    url = BASE_URL + "/api/auth/login2"

    payload = {
        "username": user.split("==")[0],
        "password": user.split("==")[1],
    }
    headeds = {"content-type": "application/x-www-form-urlencoded"}

    # check login
    response = requests.request("POST", LOGIN_URL, data=payload, headers=headeds)
    if response.status_code != 200:
        print(f"{user=} check login failed")
        print(response.status_code, response.text)
        return None

    response = requests.request("POST", url, data=payload, headers=headeds)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"{user=} get refresh token failed")
        print(response.status_code, response.text)
        return None


if __name__ == "__main__":
    max_count = 1
    count = 0
    users = get_need_refresh_user()
    for user in users:
        if count >= max_count:
            break
        refresh_token = get_refresh_token(user)
        count += 1
        if refresh_token is None:
            continue
        # 打个日志，毕竟1000额度一次:D
        logger.info(f"{user=} {refresh_token=}")
        update_and_add_to_redis(user, refresh_token)
