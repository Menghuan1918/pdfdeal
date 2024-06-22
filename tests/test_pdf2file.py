import pytest
from pdfdeal.doc2x import Doc2X
from pdfdeal.file_tools import gen_folder_list
import os
import time


def test_single_pdf2file_v1():
    client = Doc2X()
    filepath = client.pdf2file(
        pdf_file="tests/pdf/sample.pdf",
        output_path="./Output/test",
        output_names=["sample1.docx"],
        output_format="docx",
        version="v1",
    )
    assert os.path.exists(filepath[0])
    assert os.path.isfile(filepath[0])
    assert filepath[0].endswith(".docx")
    assert os.path.basename(filepath[0]) == "sample1.docx"


def test_single_pdf2file_name_error():
    client = Doc2X()
    with pytest.raises(ValueError):
        client.pdf2file(
            pdf_file="tests/pdf/sample.pdf",
            output_path="./Output/test",
            output_names=["sample1", "sample2"],
            output_format="docx",
            version="v1",
        )


def test_multiple_pdf2file_v2():
    client = Doc2X()
    file_list = gen_folder_list("tests/pdf", "pdf")
    success, failed, flag = client.pdf2file(
        pdf_file=file_list,
        output_path="./Output/test",
        output_names=["sample1.docx", "sample2.docx"],
        output_format="docx",
        version="v2",
    )
    assert flag
    assert len(success) == len(failed) == 2
    assert success[0].endswith("sample1.docx")
    assert success[1] == ""
    assert failed[0]["path"] == ""
    assert failed[1]["path"].endswith("sample_bad.pdf")


def test_multiple_high_rpm_v2():
    client = Doc2X(rpm=20, thread=10)
    start_time = time.time()
    file_list = ["tests/pdf/sample.pdf" for _ in range(25)]
    success, failed, flag = client.pdf2file(
        pdf_file=file_list,
        output_path="./Output/test",
        version="v2",
    )
    end_time = time.time()
    execution_time = end_time - start_time
    assert execution_time > 60
    assert execution_time < 120
    assert len(success) == len(failed) == 25
    for s in success:
        if s != "":
            assert os.path.exists(s)
            assert s.endswith(".md")