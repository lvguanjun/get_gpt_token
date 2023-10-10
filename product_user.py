#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   product_user.py
@Time    :   2023/10/09 19:31:53
@Author  :   lvguanjun
@Desc    :   product_user.py
"""


import json
from queue import Queue

from custom_log import logger


def product_user(file: str, q: Queue):
    processed = set()
    with open(file, "r") as f:
        for line in f.readlines():
            try:
                line = json.loads(line)
                user_name = line[0]["username"]
                password = line[0]["password"]
                if (user_name, password) in processed:
                    continue
                q.put((user_name, password))
                processed.add((user_name, password))
            except Exception as e:
                logger.error(f"{line=}\n{e=}")
                continue
    q.put(None)
    logger.info("queue add None, end")


if __name__ == "__main__":
    file = "origin.txt"
    q = Queue()
    product_user(file, q)
    print(q.get())
    print(q.qsize())
