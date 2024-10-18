from pdfdeal import Doc2X
import os
import logging

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)


def test_single_pdf2file():
    client = Doc2X(debug=True)
    filepath, _, _ = client.pdf2file(
        pdf_file="tests/pdf/sample.pdf",
        output_path="./Output/test/single/pdf2file",
        output_names=["sample1.zip"],
        output_format="md_dollor",
    )
    if filepath[0] != "":
        assert os.path.exists(filepath[0])
        assert os.path.isfile(filepath[0])
        assert filepath[0].endswith(".zip")
        assert os.path.basename(filepath[0]) == "sample1.zip"


def test_multiple_pdf2file():
    client = Doc2X(debug=True)
    success, failed, flag = client.pdf2file(
        pdf_file="tests/pdf",
        output_path="./Output/test/multiple/pdf2file",
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
