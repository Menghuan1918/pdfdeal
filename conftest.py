import pytest
import time

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_call(item):
    yield
    time.sleep(5)
