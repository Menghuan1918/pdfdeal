import pytest
from pdfdeal.doc2x import Doc2X
from pdfdeal.file_tools import gen_folder_list
import os

client = Doc2X(rpm=20)


def test_single_pic2file_v1():
    filepath = client.pic2file(
        image_file="tests/image/sample.png",
        output_path="./Output/test",
        output_names=["pic_sample1.docx"],
        output_format="docx",
    )
    if filepath[0] != "":
        assert os.path.exists(filepath[0])
        assert os.path.isfile(filepath[0])
        assert filepath[0].endswith(".docx")
        assert os.path.basename(filepath[0]) == "pic_sample1.docx"


def test_single_pic2file_name_error():
    with pytest.raises(ValueError):
        client.pic2file(
            image_file="tests/image/sample.png",
            output_path="./Output/test",
            output_names=["pic_sample1", "pic_sample2"],
            output_format="docx",
        )


def test_multiple_pic2file_v2():
    file_list = gen_folder_list("tests/image", "img")
    success, failed, flag = client.pic2file(
        image_file=file_list,
        output_path="./Output/test",
        output_names=["pic_sample1.docx", "pic_sample2.docx"],
        output_format="docx",
        version="v2",
    )
    assert flag
    assert len(success) == len(failed) == 2
    if success[0] != "":
        assert success[0].endswith("pic_sample1.docx")
    assert success[1] == ""
    assert failed[1]["path"].endswith("sample_bad.png")


def test_multiple_high_rpm_v2():
    file_list = ["tests/image/sample.png" for _ in range(15)]
    success, failed, flag = client.pic2file(
        image_file=file_list,
        output_path="./Output/test",
        version="v2",
    )
    assert len(success) == len(failed) == 15
    for s in success:
        if s != "":
            assert s.endswith(".zip")