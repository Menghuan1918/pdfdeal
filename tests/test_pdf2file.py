from pdfdeal import Doc2X
from pdfdeal import get_files
import os
import logging

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)


def test_single_pdf2file():
    client = Doc2X()
    filepath, _, _ = client.pdf2file(
        pdf_file="tests/pdf/sample.pdf",
        output_path="./Output/test/single/pdf2file",
        output_names=["sample1.docx"],
        output_format="docx",
    )
    if filepath[0] != "":
        assert os.path.exists(filepath[0])
        assert os.path.isfile(filepath[0])
        assert filepath[0].endswith(".docx")
        assert os.path.basename(filepath[0]) == "sample1.docx"


def test_multiple_pdf2file():
    client = Doc2X()
    file_list, rename = get_files("tests/pdf", "pdf", "docx")
    success, failed, flag = client.pdf2file(
        pdf_file=file_list,
        output_path="./Output/test/multiple/pdf2file",
        output_names=rename,
        output_format="docx",
    )
    assert flag
    assert len(success) == len(failed) == 3
    for s in success:
        if s != "":
            assert s.endswith("sample.docx") or s.endswith("sampleB.docx")
    for f in failed:
        if f["path"] != "":
            assert f["path"].endswith("sample_bad.pdf")


# def test_multiple_high_rpm():
#     client = Doc2X()
#     file_list = ["tests/pdf/sample.pdf" for _ in range(20)]
#     success, failed, flag = client.pdf2file(
#         pdf_file=file_list,
#         output_path="./Output/test/high_rpm/pdf2file",
#     )
#     assert len(success) == len(failed) == 20
#     i = 0
#     for s in success:
#         if s != "":
#             assert os.path.exists(s)
#             assert s.endswith(".zip")
#         else:
#             i += 1
#     print(f"===Failed {i} times===")


# def test_translate_pdf():
#     client_personal = Doc2X(apikey=os.getenv("DOC2X_APIKEY_PERSONAL"))
#     file_list = gen_folder_list("tests/pdf", "pdf")
#     success, failed, flag = client_personal.pdf_translate(file_list)
#     assert len(success) == len(failed) == 2
#     if success[0] != "":
#         assert success[0]["texts"]
#         assert success[0]["location"]
#     assert failed[1]["path"].endswith("sample_bad.pdf")
