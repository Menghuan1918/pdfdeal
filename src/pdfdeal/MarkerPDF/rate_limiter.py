import time
from threading import Lock

class RateLimiter:
    def __init__(self, qps):
        """
        初始化限流器
        
        Args:
            qps: 每秒允许的最大请求数
            提供对上传器API querys per second per thread的限制功能
        """
        self.qps = qps
        self.interval = 1.0 / qps if qps > 0 else 0
        self.last_request_time = 0
        self.lock = Lock()
    
    def acquire(self):
        """
        获取一个请求许可
        如果需要，会阻塞到下一个可用时间点
        """
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.interval:
                sleep_time = self.interval - time_since_last
                time.sleep(sleep_time)
            
            self.last_request_time = time.time() 