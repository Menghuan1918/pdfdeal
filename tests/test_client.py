from pdfdeal import Doc2X
import pytest


def test_client():
    client = Doc2X()
    assert client is not None


def test_client_with_invalid_key():
    with pytest.raises(Exception):
        Doc2X(apikey="invalid_key")


def test_client_thread():
    client = Doc2X(thread=50)
    assert client is not None


def test_client_unsupported_args():
    with pytest.raises(ValueError):
        Doc2X(rpm=1, thread=2)
