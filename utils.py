#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/10/10 00:00:05
@Author  :   lvguanjun
@Desc    :   utils.py
"""

import datetime
import json
import time

import jwt

from config import DATETIME_FORMAT


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(DATETIME_FORMAT)
        return json.JSONEncoder.default(self, obj)


def is_jwt_expired(jwt_token: str, extra_time: int = 0) -> bool:
    payload = jwt.decode(
        jwt_token, algorithms=["RS256"], options={"verify_signature": False}
    )
    exp = payload["exp"]
    return time.time() + extra_time > exp


def format_jwt_expired_time(response: dict):
    jwt_token = response["access_token"]
    payload = jwt.decode(
        jwt_token, algorithms=["RS256"], options={"verify_signature": False}
    )
    exp = payload["exp"]
    struct_time = time.localtime(exp)
    dt_object = datetime.datetime(*struct_time[:6])
    response["expired_time"] = dt_object.strftime(DATETIME_FORMAT)
    return


if __name__ == "__main__":
    pass
