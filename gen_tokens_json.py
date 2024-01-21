#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   gen_tokens_json.py
@Time    :   2023/11/15 15:03:26
@Author  :   lvguanjun
@Desc    :   gen_tokens_json.py
"""

import datetime
import json

from config import DATETIME_FORMAT
from redis_cache import gpt3_redis_cli, redis_cli


def gen_tokens_json(is_plus: bool = False):
    _redis_cli = gpt3_redis_cli
    if is_plus:
        _redis_cli = redis_cli
    tokens_json = {}
    index = 1
    for user in _redis_cli.keys("*==*"):
        token = _redis_cli.get(user)
        token = json.loads(token)
        expire_time = token["expired_time"]
        expire_time = datetime.datetime.strptime(expire_time, DATETIME_FORMAT)
        if datetime.datetime.now() > expire_time:
            continue
        if all(
            [
                not token.get("deactivated"),
                not token.get("change_password"),
                token.get("session_token"),
            ]
        ):
            user_name = token["user"].split("@")[0]
            key = user_name
            if is_plus:
                key = f" {user_name}"
            tokens_json[key] = {
                "token": token["session_token"],
                "shared": True,
                "show_user_info": True,
                "plus": is_plus,
            }
            index += 1
            if index == 101:
                break
    return tokens_json


if __name__ == "__main__":
    tokens_json_file = "tokens.json"
    is_plus = True if input("is plus? (y/n): ") == "y" else False
    tokens_json = gen_tokens_json(is_plus)
    with open(tokens_json_file, "w") as f:
        json.dump(tokens_json, f, indent=4)
