#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   other.py
@Time    :   2023/10/15 20:39:18
@Author  :   lvguanjun
@Desc    :   other.py
"""

import json
from concurrent.futures import ThreadPoolExecutor

import requests

from config import BASE_URL
from consume_user import check_is_gpt4
from pool_token import get_active_token
from redis_cache import (
    from_share_token_get_user,
    gpt3_redis_cli,
    redis_cli,
    set_to_gpt3_redis,
    set_to_redis,
)


def _check_is_gpt4(share_token, show_true=False):
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


def batch_check_is_gpt4(share_tokens, show_true=False):
    with ThreadPoolExecutor(max_workers=10) as executor:
        for share_token in share_tokens:
            executor.submit(_check_is_gpt4, share_token, show_true)


def batch_check_invite(share_tokens):
    url = BASE_URL + "/backend-api/referral/invites"
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
    sure = input("do you sure now it is gpt4 redis?? y or n: ")
    if sure != "y":
        print("thanks")
        return
    key = from_share_token_get_user(share_token, gpt3_redis_cli)
    print(key)
    value = gpt3_redis_cli.get(key)
    value = json.loads(value)
    set_to_redis(key, value)
    gpt3_redis_cli.delete(key)


def send_gpt3_to_redis2(share_token):
    sure = input("do you sure now it is gpt4 redis?? y or n: ")
    if sure != "y":
        print("thanks")
        return
    key = from_share_token_get_user(share_token)
    print(key)
    value = redis_cli.get(key)
    value = json.loads(value)
    set_to_gpt3_redis(key, value)
    redis_cli.delete(key)


def check_all_tools(token):
    url = BASE_URL + "/backend-api/models"

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            categories = response.text
            if "All Tools" in categories:
                return True
            return False
    except Exception as e:
        print(e)


def get_conversions(token: str, offest: int = 0, show_all: bool = False):
    url = BASE_URL + f"/backend-api/conversations?offset={offest}"

    limit = 50

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.request("GET", url, headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()
    for item in data["items"]:
        if item["title"] != "New chat":
            yield item["title"]
    if show_all:
        if offest + limit < data["total"]:
            yield from get_conversions(token, offest + limit, show_all)


def get_user_system_messages(token):
    url = BASE_URL + "/backend-api/user_system_messages"

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.request("GET", url, headers=headers)

    if response.status_code != 200:
        return None
    return response.json()


if __name__ == "__main__":
    active_tokens = get_active_token()

    # for token in active_tokens:
    #     if check_all_tools(token):
    #         print(token)
    #         print(from_share_token_get_user(token))

    # for token in active_tokens:
    #     for title in get_conversions(token, show_all=True):
    #         print(title)

    # for token in active_tokens:
    #     print(get_user_system_messages(token))

    batch_check_is_gpt4(active_tokens, show_true=True)
    # batch_check_invite(active_tokens)
    # send_gpt4_to_redis1("fk-uTT1JTWO8LkTl9HKK")
