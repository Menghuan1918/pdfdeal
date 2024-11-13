import os
from minio import Minio, S3Error
class MINIO:

    def __init__(self, minio_address, minio_admin, minio_password, bucket_name):
        # 通过ip 账号 密码 连接minio server
        # Http连接 将secure设置为False
        self.minioClient = Minio(endpoint=minio_address,
                                 access_key=minio_admin,
                                 secret_key=minio_password,
                                 secure=False,
                                 )
        self.bucket_name = bucket_name

    def upload_file(self, local_file_path, remote_file_path):
        """Upload a file

               Args:
                   local_file_path (str): The path of the local file to upload.
                   remote_file_path (str): The path of the remote file to upload to.

               Returns:
                   tuple: A tuple containing the URL of the uploaded file and a boolean indicating whether the upload was successful.
        """
        # 桶是否存在 不存在则新建
        check_bucket = self.minioClient.bucket_exists(self.bucket_name)
        if not check_bucket:
            self.minioClient.make_bucket(self.bucket_name)
        try:
            path, file_name = os.path.split(local_file_path)
            self.minioClient.fput_object(bucket_name=self.bucket_name,
                                         object_name=file_name,
                                         file_path=local_file_path)
            remote_file_path = "http://127.0.0.1:9000" + '/' + self.bucket_name + '/' + file_name
            return (remote_file_path, True)
        except FileNotFoundError as err:
            print('upload_failed: ' + str(err))
        except S3Error as err:
            print("upload_failed:", err)

def Min(minio_address, minio_admin, minio_password, bucket_name) -> callable:
        Min_uploader = MINIO(
        minio_address = minio_address,
        minio_admin = minio_admin,
        minio_password = minio_password,
        bucket_name = bucket_name)
        return Min_uploader.upload_file







