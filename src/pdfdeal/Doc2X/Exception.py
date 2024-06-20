class RateLimit(Exception):
    """
    达到每分钟最大请求次数
    """
    pass