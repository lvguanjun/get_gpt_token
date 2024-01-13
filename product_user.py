#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   product_user.py
@Time    :   2023/10/09 19:31:53
@Author  :   lvguanjun
@Desc    :   product_user.py
"""


import json
from collections import deque

from custom_log import logger


def error_handler(func):
    def wrapper(line):
        try:
            return func(line)
        except Exception as e:
            logger.error(f"{line=}\n{e=}")
            return iter([])

    return wrapper


@error_handler
def deal_json(line):
    line = json.loads(line)
    return ((item["username"], item["password"]) for item in line)


@error_handler
def deal_4_line(line):
    user, password = line.split("----", 1)
    return iter([(user, password)])


@error_handler
def deal_2_equal(line):
    user, password = line.split("==", 1)
    return iter([(user, password)])


def product_user(file: str, q: deque):
    processed = set()
    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "----" in line:
                for item in deal_4_line(line):
                    if item in processed:
                        continue
                    q.append(item)
                    processed.add(item)
            elif "==" in line:
                for item in deal_2_equal(line):
                    if item in processed:
                        continue
                    q.append(item)
                    processed.add(item)
            else:
                for item in deal_json(line):
                    if item in processed:
                        continue
                    q.append(item)
                    processed.add(item)
    q.appendleft(None)
    logger.info("queue add None, end")


if __name__ == "__main__":
    file = "origin.txt"
    q = Queue()
    product_user(file, q)
    print(q.get())
    print(q.qsize())
