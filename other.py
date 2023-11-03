#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   other.py
@Time    :   2023/10/15 20:39:18
@Author  :   lvguanjun
@Desc    :   other.py
"""

import json

import requests

from consume_user import check_is_gpt4
from pool_token import get_active_token
from redis_cache import (
    from_share_token_get_user,
    gpt3_redis_cli,
    redis_cli,
    set_to_gpt3_redis,
    set_to_redis,
)


def batch_check_is_gpt4(share_tokens, show_true=False):
    for share_token in share_tokens:
        try:
            if not check_is_gpt4(share_token):
                if show_true:
                    print("false")
                else:
                    print("false", share_token)
            else:
                if show_true:
                    print("true", share_token)
                else:
                    print("true")
        except Exception as e:
            print(e)
            print(share_token, "exception")


def batch_check_invite(share_tokens):
    url = "https://ai.fakeopen.com/api/referral/invites"
    try:
        for token in share_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.request("GET", url, headers=headers)
            if response.status_code == 200:
                resp_dict = response.json()
                invite_codes = resp_dict["invite_codes"]
                if invite_codes:
                    print(f"{token=}\n{resp_dict}")
                else:
                    print(f"not claimed_invites and invite_codes")
                    pass
            else:
                print(response.status_code, response.text)
    except Exception as e:
        print(e)


def send_gpt4_to_redis1(share_token):
    key = from_share_token_get_user(share_token, gpt3_redis_cli)
    value = gpt3_redis_cli.get(key)
    value = json.loads(value)
    set_to_redis(key, value)
    gpt3_redis_cli.delete(key)


def send_gpt3_to_redis2(share_token):
    key = from_share_token_get_user(share_token)
    value = redis_cli.get(key)
    value = json.loads(value)
    set_to_gpt3_redis(key, value)
    redis_cli.delete(key)


def check_all_tools(token):
    url = "https://ai.fakeopen.com/api/models"

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            categories = response.text
            if "All Tools" in categories:
                return True
            return False
        raise Exception(f"{response.status_code=}, {response.text=}")
    except Exception as e:
        raise Exception(f"{e=}")


if __name__ == "__main__":
    active_tokens = get_active_token()
    batch_check_is_gpt4(active_tokens)
    batch_check_invite(active_tokens)
    # send_gpt4_to_redis1("fk-zuFrj9ayZ0HaZKn9Xh4zzCA_hA")
