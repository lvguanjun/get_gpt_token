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


def gen_tokens_json(is_plus: bool = False, max_index: int = 100):
    if max_index <= 0:
        return {}
    _redis_cli = gpt3_redis_cli
    if is_plus:
        _redis_cli = redis_cli
    tokens_json = {}
    index = 0
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
            if index == max_index:
                break
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
    return tokens_json


if __name__ == "__main__":
    tokens_json_file = "tokens.json"
    max_index = 100
    plus_tokens = gen_tokens_json(is_plus=True)
    not_plus_tokens = gen_tokens_json(
        is_plus=False, max_index=max_index - len(plus_tokens)
    )
    tokens_json = {**plus_tokens, **not_plus_tokens}
    with open(tokens_json_file, "w") as f:
        json.dump(tokens_json, f, indent=4)
