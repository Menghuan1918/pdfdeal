import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import logging


class S3_Settings:
    def __init__(
        self,
        S3_ACCESS_KEY_ID,
        S3_ACCESS_KEY_SECRET,
        Endpoint,
        Bucket,
        Customized_Domain,
    ):
        """Initialize the S3 client.

        Args:
            S3_ACCESS_KEY_ID (str): The access key ID for S3.
            S3_ACCESS_KEY_SECRET (str): The access key secret for S3.
            Endpoint (str): The endpoint for S3.
            Bucket (str): The name of the bucket to upload to.
            Customized_Domain (str): The customized domain for the S3 bucket. **Note the URL of the imgs will be `{Customized_Domain}/{remote_file_path}`**
        """
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=Endpoint,
            aws_access_key_id=S3_ACCESS_KEY_ID,
            aws_secret_access_key=S3_ACCESS_KEY_SECRET,
        )
        self.bucket = Bucket
        self.customized_domain = Customized_Domain

    def upload_file(self, local_file_path, remote_file_path):
        """Upload a file to S3.

        Args:
            local_file_path (str): The path of the local file to upload.
            remote_file_path (str): The path of the remote file to upload to.

        Returns:
            tuple: A tuple containing the URL of the uploaded file and a boolean indicating whether the upload was successful.
        """
        try:
            self.s3_client.upload_file(
                local_file_path,
                self.bucket,
                remote_file_path,
                ExtraArgs={"ACL": "public-read"},
            )
            # * Default think the bucket is public read
            return (
                f"{self.customized_domain}/{remote_file_path}",
                True,
            )
        except (NoCredentialsError, ClientError) as e:
            logging.exception(f"Error to upload the file: {local_file_path}, {e}")
            return e, False


def S3(
    S3_ACCESS_KEY_ID, S3_ACCESS_KEY_SECRET, Endpoint, Bucket, Customized_Domain
) -> callable:
    """Initialize the S3 client and return a callable function to upload files.

    Args:
        S3_ACCESS_KEY_ID (str): The access key ID for S3.
        S3_ACCESS_KEY_SECRET (str): The access key secret for S3.
        Endpoint (str): The endpoint for S3.
        Bucket (str): The name of the bucket to upload to.
        Customized_Domain (str): The customized domain for the S3 bucket. **Note the URL of the imgs will be `{Customized_Domain}/{remote_file_path}`**

    Returns:
        callable: The upload_file method of the S3 client.
    """
    s3_uploader = S3_Settings(
        S3_ACCESS_KEY_ID=S3_ACCESS_KEY_ID,
        S3_ACCESS_KEY_SECRET=S3_ACCESS_KEY_SECRET,
        Endpoint=Endpoint,
        Bucket=Bucket,
        Customized_Domain=Customized_Domain,
    )
    return s3_uploader.upload_file
