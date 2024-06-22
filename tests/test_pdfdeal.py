from pdfdeal.doc2x import Doc2X
from pdfdeal.file_tools import gen_folder_list
import os

client = Doc2X(rpm=20)


def test_pdfdeal_v1():
    filepath = client.pdfdeal(
        input="tests/pdf/sample.pdf",
        path="./Output/test",
    )
    if filepath[0] != "":
        assert os.path.exists(filepath[0])
        assert os.path.isfile(filepath[0])
        assert filepath[0].endswith(".pdf")
        assert os.path.basename(filepath[0]) == "sample.pdf"


def test_multiple_pdfdeal_v2():
    file_list = gen_folder_list("tests/pdf", "pdf")
    success, failed, flag = client.pdfdeal(
        input=file_list,
        path="./Output/test",
        version="v2",
    )
    assert flag
    assert len(success) == len(failed) == 2
    if success[0] != "":
        assert success[0].endswith("sample.pdf")
    assert success[1] == ""
    assert failed[1]["path"].endswith("sample_bad.pdf")
