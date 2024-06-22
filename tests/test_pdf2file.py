import pytest
from pdfdeal.doc2x import Doc2X
import os

def test_single_pdf2file_v1():
    client = Doc2X()
    filepath = client.pdf2file(
        pdf_file="tests/pdf/sample.pdf",
        output_path="./Output/test",
        output_names=["sample1.docx"],
        output_format="docx",
        version="v1"
    )
    assert os.path.exists(filepath[0])
    assert os.path.isfile(filepath[0])
    assert filepath[0].endswith(".docx")
    assert os.path.basename(filepath[0]) == "sample1.docx"

def test_single_pdf2file_name_error():
    client = Doc2X()
    with pytest.raises(ValueError):
        client.pdf2file(
            pdf_file="tests/sample.pdf",
            output_path="./Output/test",
            output_names=["sample1", "sample2"],
            output_format="docx",
            version="v1"
        )