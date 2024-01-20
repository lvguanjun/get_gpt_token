#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   load_session.py
@Time    :   2024/01/21 02:13:51
@Author  :   lvguanjun
@Desc    :   load_session.py
"""

import json
from concurrent.futures import ThreadPoolExecutor

import requests

from config import BASE_URL
from consume_user import check_is_gpt4
from redis_cache import set_to_gpt3_redis, set_to_redis
from session_refresh import session_refresh


def get_session(file):
    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or "session_token" not in line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                print(line)
                continue


def get_user_email(token):
    url = BASE_URL + "/backend-api/me"
    headeds = {"Authorization": f"Bearer {token}"}
    response = requests.request("GET", url, headers=headeds)
    if response.status_code == 200:
        return response.json().get("email")
    else:
        print(response.status_code, response.text)


def check_session(session_token):
    if session_token := session_token.get("session_token"):
        response = session_refresh(session_token)
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get("access_token")
            user = get_user_email(access_token) + "==mock_password"
            is_gpt4 = check_is_gpt4(access_token)
            if is_gpt4:
                print("add gpt4 to redis")
                set_to_redis(user, token_info)
            else:
                print("add gpt3 to redis")
                set_to_gpt3_redis(user, token_info)
        else:
            print(response.status_code, response.text)


if __name__ == "__main__":
    file = "res.txt"
    with ThreadPoolExecutor(max_workers=10) as executor:
        for session_token in get_session(file):
            executor.submit(check_session, session_token)
