from pdfdeal.doc2x import Doc2X
import os

def test_client():
    client = Doc2X()
    assert client is not None


def test_client_with_personal_key():
    client = Doc2X(apikey=os.getenv("DOC2X_APIKEY_PERSONAL"))
    assert client is not None