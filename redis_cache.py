#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   redis_cache.py
@Time    :   2023/10/09 22:21:09
@Author  :   lvguanjun
@Desc    :   redis_cache.py
"""

import datetime
import json
from typing import Optional

from config import DATETIME_FORMAT, TOKEN_EXPIRE_EXTRA_TIME, gpt3_redis_cli, redis_cli
from utils import Encoder, format_jwt_expired_time, is_jwt_expired


def set_to_redis(key: str, value: dict):
    format_jwt_expired_time(value)
    value["user"] = key
    value = json.dumps(value, cls=Encoder)
    redis_cli.set(key, value)


def update_and_add_to_redis(key: str, value: dict):
    origin_value = redis_cli.get(key)
    origin_value = json.loads(origin_value) if origin_value else {}
    if "access_token" in value:
        format_jwt_expired_time(value)
    origin_value.update(value)
    # 去除值为None的键值对
    origin_value = {k: v for k, v in origin_value.items() if v is not None}
    res = json.dumps(origin_value, cls=Encoder)
    redis_cli.set(key, res)


def set_to_gpt3_redis(key: str, value: dict):
    format_jwt_expired_time(value)
    value["user"] = key
    value = json.dumps(value, cls=Encoder)
    gpt3_redis_cli.set(key, value)


def update_and_add_to_redis_gpt3(key: str, value: dict):
    origin_value = gpt3_redis_cli.get(key)
    origin_value = json.loads(origin_value) if origin_value else {}
    if "access_token" in value:
        format_jwt_expired_time(value)
    origin_value.update(value)
    # 去除值为None的键值对
    origin_value = {k: v for k, v in origin_value.items() if v is not None}
    res = json.dumps(origin_value, cls=Encoder)
    gpt3_redis_cli.set(key, res)


def get_from_redis(key: str, cli=redis_cli) -> Optional[dict]:
    value = cli.get(key)
    if value is not None:
        value = json.loads(value)
        jwt_token = value["access_token"]
        if is_jwt_expired(jwt_token, TOKEN_EXPIRE_EXTRA_TIME):
            return None
    return value


def set_error_to_redis(key: str):
    redis_cli.sadd("error-user", key)


def is_in_error_set(key: str) -> bool:
    return redis_cli.sismember("error-user", key)


def get_need_refresh_tokens(extra_time: int = 0) -> list:
    """
    获取需要刷新的token

    @param extra_time: 提前过期时间，如果小于0，则获取所有token
    """
    need_refresh_tokens = []
    for user in redis_cli.keys("*==*"):
        token = redis_cli.get(user)
        token = json.loads(token)
        if token.get("change_password"):
            continue
        if extra_time < 0:
            need_refresh_tokens.append((user, token))
            continue
        expire_time = token["expired_time"]
        expire_time = datetime.datetime.strptime(expire_time, DATETIME_FORMAT)
        if (
            datetime.datetime.now() + datetime.timedelta(seconds=extra_time)
            < expire_time
        ):
            need_refresh_tokens.append((user, token))
    return need_refresh_tokens


def get_all_token(extra_time: int = 0) -> list:
    """
    获取所有token

    @param extra_time: 提前过期时间，如果小于0，则获取所有token
    """
    all_tokens = []
    for user in redis_cli.keys("*==*"):
        token = redis_cli.get(user)
        token = json.loads(token)
        if extra_time < 0:
            all_tokens.append(token)
            continue
        expire_time = token["expired_time"]
        expire_time = datetime.datetime.strptime(expire_time, DATETIME_FORMAT)
        if (
            datetime.datetime.now() + datetime.timedelta(seconds=extra_time)
            < expire_time
        ):
            all_tokens.append(token)
    return all_tokens


def get_survive_share_token(extra_time: int = 0) -> list:
    """
    获取所有幸存的的share_token
    """
    survive_tokens = []
    for user in redis_cli.keys("*==*"):
        token = redis_cli.get(user)
        token = json.loads(token)
        # expire_time = token["expired_time"]
        # expire_time = datetime.datetime.strptime(expire_time, DATETIME_FORMAT)
        # if (
        #     datetime.datetime.now() + datetime.timedelta(seconds=extra_time)
        #     > expire_time
        # ):
        #     continue
        if all(
            [
                not token.get("change_password"),
                not token.get("deactivated"),
                # token.get("refresh_token"),
            ]
        ):
            survive_tokens.append(token["share_token"])
    return survive_tokens, len(survive_tokens)


def from_share_token_get_user(share_token: str, redis_cli=redis_cli) -> Optional[str]:
    """
    通过share_token获取user
    """
    for user in redis_cli.keys("*==*"):
        token = redis_cli.get(user)
        token = json.loads(token)
        if token.get("share_token") == share_token:
            return user
    return None


if __name__ == "__main__":
    survive_tokens, count = get_survive_share_token()
    print(f"{survive_tokens=}", f"{count=}", sep="\n")
