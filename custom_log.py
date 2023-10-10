#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   custom_log.py
@Time    :   2023/10/09 19:32:00
@Author  :   lvguanjun
@Desc    :   custom_log.py
"""


import logging
from config import DEBUG_MODULE

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s %(filename)s %(levelname)s]  %(message)s", "%Y-%m-%d %H:%M:%S"
)

file_handler = logging.FileHandler("log.txt")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

if DEBUG_MODULE:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
