from pdfdeal import Doc2X
import os
import pytest


def test_single_pdf2file():
    client = Doc2X(debug=True, thread=1)
    filepath, failed, flag = client.pdf2file(
        pdf_file="tests/pdf/sample.pdf",
        output_path="./Output/test/single/pdf2file",
        output_names=["Test.zip"],
        output_format="md_dollar",
    )
    if filepath[0] != "":
        assert os.path.exists(filepath[0])
        assert os.path.isfile(filepath[0])
        assert filepath[0].endswith(".zip")
        assert os.path.basename(filepath[0]) == "Test.zip"
    print(filepath)
    print(failed)
    print(flag)


def test_error_input_pdf2file():
    client = Doc2X(debug=True, thread=1)
    with pytest.raises(ValueError):
        client.pdf2file(
            pdf_file="tests/pdf/sample.pdf",
            output_path="./Output/test/single/pdf2file",
            output_names=["sample1.zip"],
            output_format="md_dallar",
        )


def test_multiple_pdf2file():
    client = Doc2X(debug=True, thread=1)
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
    print(success)
    print(failed)
    print(flag)


def test_all_fail_pdf2file():
    client = Doc2X(debug=True, thread=1)
    success, failed, flag = client.pdf2file(
        pdf_file="tests/pdf/sample_bad.pdf",
        output_path="./Output/test/allfail/pdf2file",
        output_format="md",
    )
    assert flag
    assert len(success) == 1
    assert len(failed) == 1
    print(success)
    print(failed)
    print(flag)


def test_multiple_outtypes():
    client = Doc2X(debug=True, thread=1)
    success, failed, flag = client.pdf2file(
        pdf_file="tests/pdf/sample.pdf",
        output_path="./Output/test/multiple_outtypes/pdf2file",
        output_names=[["sample1.docx", "sample2.zip"]],
        output_format="docx,md",
    )
    assert len(success) == 1
    assert len(failed) == 1
    for s in success:
        if isinstance(s, list):
            for i in s:
                assert i.endswith("sample1.docx") or i.endswith("sample2.zip")
    print(success)
    print(failed)
    print(flag)
