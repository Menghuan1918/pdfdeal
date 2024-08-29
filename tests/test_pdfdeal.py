from pdfdeal import Doc2X
from pdfdeal.file_tools import get_files
import os
import logging

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)


def test_pdfdeal():
    client = Doc2X()
    filepath, _, _ = client.pdfdeal(
        pdf_file="tests/pdf/sample.pdf",
        output_path="./Output/test/pdfdeal",
    )
    if filepath[0] != "":
        assert os.path.exists(filepath[0])
        assert os.path.isfile(filepath[0])
        assert filepath[0].endswith(".pdf")


def test_multiple_pdfdeal():
    client = Doc2X()
    file_list, rename = get_files("tests/pdf", "pdf", "pdf")
    success, failed, flag = client.pdfdeal(
        pdf_file=file_list,
        output_path="./Output/test/multiple/pdfdeal",
        output_names=rename,
    )
    assert flag
    assert len(success) == len(failed) == 3
    for s in success:
        if s != "":
            assert s.endswith(".pdf")
    for f in failed:
        if f["path"] != "":
            assert f["path"].endswith("sample_bad.pdf")


# def test_multiple_high_rpm_v2():
#     client = Doc2X()
#     file_list = ["tests/pdf/sample.pdf" for _ in range(20)]
#     success, failed, flag = client.pdfdeal(
#         input=file_list,
#         path="./Output/test/high_rpm/pdfdeal",
#     )
#     assert len(success) == len(failed) == 20
#     i = 0
#     for s in success:
#         if s != "":
#             assert os.path.exists(s)
#             assert s.endswith(".pdf")
#         else:
#             i += 1
#     print(f"===Failed {i} times===")
