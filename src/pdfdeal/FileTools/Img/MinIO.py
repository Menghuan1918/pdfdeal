import os
from minio import Minio, S3Error
import logging
from urllib.parse import urlparse
import json


class MINIO:
    def __init__(self, minio_address, minio_admin, minio_password, bucket_name):
        # 通过ip 账号 密码 连接minio server
        # 根据地址自动判断是否使用安全连接
        parsed_url = urlparse(minio_address)
        secure = parsed_url.scheme == "https"
        self.minioClient = Minio(
            endpoint=parsed_url.netloc,
            access_key=minio_admin,
            secret_key=minio_password,
            secure=secure,
        )
        self.bucket_name = bucket_name
        self.minio_address = minio_address

    def upload_file(self, local_file_path, remote_file_path):
        """Upload a file

        Args:
            local_file_path (str): The path of the local file to upload.
            remote_file_path (str): The path of the remote file to upload to.

        Returns:
            tuple: A tuple containing the URL of the uploaded file and a boolean indicating whether the upload was successful.
        """
        # 检查桶是否存在，不存在则新建并设置为公开只读
        check_bucket = self.minioClient.bucket_exists(self.bucket_name)
        if not check_bucket:
            self.minioClient.make_bucket(self.bucket_name)
            # 设置桶策略为公开只读
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                        "Resource": f"arn:aws:s3:::{self.bucket_name}",
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.bucket_name}/*",
                    },
                ],
            }
            self.minioClient.set_bucket_policy(self.bucket_name, json.dumps(policy))
        try:
            path, file_name = os.path.split(local_file_path)
            self.minioClient.fput_object(
                bucket_name=self.bucket_name,
                object_name=file_name,
                file_path=local_file_path,
            )
            parsed_url = urlparse(self.minio_address)
            scheme = parsed_url.scheme or "http"
            remote_file_path = (
                f"{scheme}://{parsed_url.netloc}/{self.bucket_name}/{file_name}"
            )
            return (remote_file_path, True)
        except FileNotFoundError as err:
            logging.exception(f"Error to upload the file: {local_file_path}, {err}")
            return err, False
        except S3Error as err:
            logging.exception(f"Error to upload the file: {local_file_path}, {err}")
            return err, False


def Min(minio_address, minio_admin, minio_password, bucket_name) -> callable:
    Min_uploader = MINIO(
        minio_address=minio_address,
        minio_admin=minio_admin,
        minio_password=minio_password,
        bucket_name=bucket_name,
    )
    return Min_uploader.upload_file
