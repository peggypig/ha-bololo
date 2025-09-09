# -*- coding: utf-8 -*-
import asyncio
from concurrent.futures import ThreadPoolExecutor


def sync_call(call):
    """
    同步方式调用协程函数
    自动判断是否有事件循环，选择合适的方式执行
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # 没有运行的事件循环 → 直接 asyncio.run
        return asyncio.run(call)
    else:
        # 有事件循环 → 用线程隔离运行
        with ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, call)
            return future.result()
