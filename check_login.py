#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   check_login.py
@Time    :   2023/12/28 22:59:05
@Author  :   lvguanjun
@Desc    :   check_login.py
"""

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

from config import DATETIME_FORMAT, LOGIN_URL
from redis_cache import redis_cli, set_error_to_redis, update_and_add_to_redis


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
            is_expired = True
        else:
            is_expired = False
        if redis_cli.sismember("error-user", user):
            # # 从 error-uesr 删除
            # redis_cli.srem("error-user", user)
            print(f"{user=} in error set")
            continue
        if any(
            [
                token.get("change_password"),
                token.get("deactivated"),
            ]
        ):
            users.append((user, is_expired))
    return users


def check_login(user, is_expired):
    payload = {
        "username": user.split("==")[0],
        "password": user.split("==")[1],
    }
    headeds = {"content-type": "application/x-www-form-urlencoded"}

    # check login
    response = requests.request("POST", LOGIN_URL, data=payload, headers=headeds)
    if response.status_code != 200:
        response_text = response.text
        if "wrong username or password" in response_text:
            print(f"{user=} wrong username or password")
            set_error_to_redis(user)
            if is_expired:
                print(f"{user=} is expired, and delete")
                redis_cli.delete(user)
            return False
        elif "been deleted or deactivated" in response_text:
            print(f"{user=} been deleted or deactivated")
            set_error_to_redis(user)
            redis_cli.delete(user)
            return False
        print(f"{user=} check login failed")
        print(response.status_code, response.text)
        return False
    response = response.json()
    response["change_password"] = None
    response["deactivated"] = None
    update_and_add_to_redis(user, response)
    print(f"{user=} check login success")


if __name__ == "__main__":
    users = get_need_refresh_user()
    for user, is_expired in users:
        check_login(user, is_expired)
        # break
