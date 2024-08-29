import oss2
import logging


class OSS:
    def __init__(self, OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, Endpoint, Bucket):
        """Initialize the OSS client.

        Args:
            OSS_ACCESS_KEY_ID (str): The access key ID for Aliyun OSS.
            OSS_ACCESS_KEY_SECRET (str): The access key secret for Aliyun OSS.
            Endpoint (str): The endpoint for Aliyun OSS.
            Bucket (str): The name of the bucket to upload to.
        """
        self.auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
        self.bucket = oss2.Bucket(self.auth, Endpoint, Bucket)

    def upload_file(self, local_file_path, remote_file_path):
        """Upload a file to Aliyun OSS.

        Args:
            local_file_path (str): The path of the local file to upload.
            remote_file_path (str): The path of the remote file to upload to.

        Returns:
            tuple: A tuple containing the URL of the uploaded file and a boolean indicating whether the upload was successful.
        """
        try:
            self.bucket.put_object_from_file(remote_file_path, local_file_path)
            # * Default think the bucket is public read
            return (
                f"https://{self.bucket.bucket_name}.{self.bucket.endpoint.split('://')[1]}/{remote_file_path}",
                True,
            )
        except Exception as e:
            logging.error(f"Error to upload the file: {local_file_path}, {e}")
            return e, False


def Ali_OSS(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, Endpoint, Bucket) -> callable:
    """Initialize the OSS client and return a callable function to upload files.

    Args:
        OSS_ACCESS_KEY_ID (str): The access key ID for Aliyun OSS.
        OSS_ACCESS_KEY_SECRET (str): The access key secret for Aliyun OSS.
        Endpoint (str): The endpoint for Aliyun OSS.
        Bucket (str): The name of the bucket to upload to.

    Returns:
        callable: The upload_file method of the OSS client.
    """
    ali_oss = OSS(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, Endpoint, Bucket)
    return ali_oss.upload_file
