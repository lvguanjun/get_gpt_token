#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   conversation_check.py
@Time    :   2024/01/09 17:17:36
@Author  :   lvguanjun
@Desc    :   conversation_check.py
"""


import requests

from config import BASE_URL
from redis_cache import get_survive_share_token


def check_conversation(conversation_id, token):
    url = BASE_URL + f"/backend-api/conversation/{conversation_id}"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        return True
    return False


if __name__ == "__main__":
    tokens, _ = get_survive_share_token()
    for token in tokens:
        conversation_id = "0c24a2e3-650d-4f29"
        check_res = check_conversation(conversation_id, token)
        if check_res:
            print(token)
            break
