"""Redis 分布式锁：防止并发冲突。"""

import time
import uuid
from contextlib import contextmanager

from app.core.redis import get_redis_client


@contextmanager
def redis_lock(key: str, timeout: int = 10, retry_interval: float = 0.1, max_retries: int = 30):
    """获取 Redis 分布式锁，超时则抛出异常。

    Args:
        key: 锁的键名
        timeout: 锁的过期时间（秒）
        retry_interval: 重试间隔（秒）
        max_retries: 最大重试次数
    """
    redis = get_redis_client()
    lock_value = str(uuid.uuid4())
    lock_key = f"lock:{key}"

    # 尝试获取锁
    for _ in range(max_retries):
        if redis.set(lock_key, lock_value, nx=True, ex=timeout):
            try:
                yield lock_value
                return
            finally:
                # 释放锁：只释放自己持有的锁
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                redis.eval(lua_script, 1, lock_key, lock_value)
        time.sleep(retry_interval)

    raise RuntimeError(f"无法获取锁: {key}")
