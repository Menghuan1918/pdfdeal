import oss2


class OSS:
    def __init__(self, OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, Endpoint, Bucket):
        self.auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
        self.bucket = oss2.Bucket(self.auth, Endpoint, Bucket)

    def upload_file(self, local_file_path, remote_file_path):
        """
        Upload a file to Aliyun OSS
        :param local_file_path: local file path
        :param remote_file_path: remote file path
        :return: remote file url
        """
        try:
            self.bucket.put_object_from_file(remote_file_path, local_file_path)
            # * Default think the bucket is public read
            return (
                f"https://{self.bucket.bucket_name}.{self.bucket.endpoint.split('://')[1]}/{remote_file_path}",
                True,
            )
        except Exception as e:
            print(f"Error to upload the file: {local_file_path}, {e}")
            return e, False


def Ali_OSS(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, Endpoint, Bucket) -> callable:
    ali_oss = OSS(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, Endpoint, Bucket)
    return ali_oss.upload_file
