#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   gen_tokens_json.py
@Time    :   2023/11/15 15:03:26
@Author  :   lvguanjun
@Desc    :   gen_tokens_json.py
"""

import json

from redis_cache import redis_cli


def get_share_token_session_token_map():
    share_token_session_token_map = {}
    for user in redis_cli.keys("*==*"):
        token = redis_cli.get(user)
        token = json.loads(token)
        if share_token := token.get("share_token"):
            if session_token := token.get("session_token") or token.get(
                "refresh_token"
            ):
                share_token_session_token_map[share_token] = session_token
                continue
        print(
            f'invalid token: {token.get("user")},'
            f" share_token={share_token is not None},"
            f" session_token={session_token is not None}"
        )
    return share_token_session_token_map


def gen_tokens_json(share_tokens: list[str], share_token_session_token_map: dict):
    tokens_json = {}
    for index, token in enumerate(share_tokens):
        if session_token := share_token_session_token_map.get(token):
            tokens_json[f"user{index}"] = {
                "token": session_token,
                "shared": True,
                "show_user_info": True,
                "plus": True,
            }
    return tokens_json


if __name__ == "__main__":
    share_tokens_file = "effective_tokens.txt"
    tokens_json_file = "tokens.json"
    with open(share_tokens_file) as f:
        share_tokens = json.load(f)
    share_token_session_token_map = get_share_token_session_token_map()
    tokens_json = gen_tokens_json(share_tokens, share_token_session_token_map)
    with open(tokens_json_file, "w") as f:
        json.dump(tokens_json, f, indent=4)
