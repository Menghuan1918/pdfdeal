from pdfdeal.doc2x import Doc2X
from pdfdeal.file_tools import gen_folder_list
import os



def test_single_pic2file_v1():
    client = Doc2X()
    filepath = client.pic2file(
        image_file="tests/image/sample.png",
        output_path="./Output/test/single/pic2file",
        output_names=["pic_sample1.docx"],
        output_format="docx",
    )
    if filepath[0] != "":
        assert os.path.exists(filepath[0])
        assert os.path.isfile(filepath[0])
        assert filepath[0].endswith(".docx")
        assert os.path.basename(filepath[0]) == "pic_sample1.docx"




def test_multiple_pic2file_v2():
    client = Doc2X()
    file_list = gen_folder_list("tests/image", "img")
    success, failed, flag = client.pic2file(
        image_file=file_list,
        output_path="./Output/test/multiple/pic2file",
        output_names=["pic_sample1.docx", "pic_sample2.docx"],
        output_format="docx",
        version="v2",
    )
    assert flag
    assert len(success) == len(failed) == 2
    for s in success:
        if s != "":
            assert s.endswith("pic_sample1.docx") or s.endswith("pic_sample2.docx")
    for f in failed:
        if f ["path"]!= "":
            assert f["path"].endswith("sample_bad.png")


# def test_multiple_high_rpm_v2():
#     client = Doc2X()
#     file_list = ["tests/image/sample.png" for _ in range(20)]
#     success, failed, flag = client.pic2file(
#         image_file=file_list,
#         output_path="./Output/test",
#         version="v2",
#     )
#     assert len(success) == len(failed) == 20
#     i = 0
#     for s in success:
#         if s != "":
#             assert s.endswith(".zip")
#         else:
#             i += 1
#     print(f"===Failed {i} times===")