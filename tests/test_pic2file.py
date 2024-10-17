# from pdfdeal import Doc2X
# from pdfdeal.file_tools import get_files
# import os
# import logging

# httpx_logger = logging.getLogger("httpx")
# httpx_logger.setLevel(logging.WARNING)
# logging.basicConfig(level=logging.INFO)


# def test_single_pic2file():
#     client = Doc2X()
#     filepath, _, _ = client.pic2file(
#         image_file="tests/image/sample.png",
#         output_path="./Output/test/single/pic2file",
#         output_names=["pic_sample1.docx"],
#         output_format="docx",
#     )
#     if filepath[0] != "":
#         assert os.path.exists(filepath[0])
#         assert os.path.isfile(filepath[0])
#         assert filepath[0].endswith(".docx")
#         assert os.path.basename(filepath[0]) == "pic_sample1.docx"


# def test_multiple_pic2file():
#     client = Doc2X()
#     file_list, rename = get_files("tests/image", "img", "docx")
#     success, failed, flag = client.pic2file(
#         image_file=file_list,
#         output_path="./Output/test/multiple/pic2file",
#         output_names=rename,
#         output_format="docx",
#     )
#     assert flag
#     assert len(success) == len(failed) == 3
#     for s in success:
#         if s != "":
#             assert s.endswith("sample1.docx") or s.endswith("sample.docx")


# # def test_multiple_high_rpm():
# #     client = Doc2X()
# #     file_list = ["tests/image/sample.png" for _ in range(20)]
# #     success, failed, flag = client.pic2file(
# #         image_file=file_list,
# #         output_path="./Output/test",
# #     )
# #     assert len(success) == len(failed) == 20
# #     i = 0
# #     for s in success:
# #         if s != "":
# #             assert s.endswith(".zip")
# #         else:
# #             i += 1
# #     print(f"===Failed {i} times===")
