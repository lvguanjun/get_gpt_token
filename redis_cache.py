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

from config import DATETIME_FORMAT, TOKEN_EXPIRE_EXTRA_TIME, redis_cli
from utils import Encoder, is_jwt_expired, format_jwt_expired_time


def set_to_redis(key: str, value: dict):
    format_jwt_expired_time(value)
    value = json.dumps(value, cls=Encoder)
    redis_cli.set(key, value)


def get_from_redis(key: str) -> Optional[dict]:
    value = redis_cli.get(key)
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
        expire_time = token["expired_time"]
        expire_time = datetime.datetime.strptime(expire_time, DATETIME_FORMAT)
        if extra_time < 0:
            need_refresh_tokens.append((user, token))
            continue
        if (
            datetime.datetime.now() + datetime.timedelta(seconds=extra_time)
            > expire_time
        ):
            need_refresh_tokens.append((user, token))
    return need_refresh_tokens
