#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2023/10/10 00:49:49
@Author  :   lvguanjun
@Desc    :   main.py
"""

from product_user import product_user
from consume_user import consume_user

from queue import Queue
import threading

if __name__ == "__main__":
    # 请求限速3/min"
    sleep_time = 25
    file = "origin.txt"
    q = Queue()
    p_t = threading.Thread(target=product_user, args=(file, q))
    c_t = threading.Thread(target=consume_user, args=(q, sleep_time))
    p_t.start()
    c_t.start()
    p_t.join()
    c_t.join()
