#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2023/10/10 00:49:49
@Author  :   lvguanjun
@Desc    :   main.py
"""

import threading
from queue import Queue

from consume_user import consume_user
from product_user import product_user

if __name__ == "__main__":
    # 请求限速6/min"
    sleep_time = 0
    file = "origin.txt"
    max_consume = 10
    q = Queue()
    p_t = threading.Thread(target=product_user, args=(file, q))
    c_t = threading.Thread(target=consume_user, args=(q, sleep_time, max_consume))
    p_t.start()
    c_t.start()
    p_t.join()
    c_t.join()
