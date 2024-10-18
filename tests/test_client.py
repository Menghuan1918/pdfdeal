import logging.config
from pdfdeal import Doc2X
import logging

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)


def test_client():
    client = Doc2X()
    assert client is not None
