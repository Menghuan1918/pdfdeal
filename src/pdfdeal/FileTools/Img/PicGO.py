import httpx
import logging


class PicGO_Settings:
    def __init__(self, endpoint="http://127.0.0.1:36677"):
        """Initialize the PicGO client.

        Args:
            endpoint (str): The endpoint for PicGO API. Defaults to "http://127.0.0.1:36677".
        """
        self.endpoint = endpoint

    def upload_file(self, local_file_path, remote_file_path=None):
        """Upload a file to PicGO.

        Args:
            local_file_path (str): The path of the local file to upload.
            remote_file_path (str): Not used in PicGO, kept for interface consistency.

        Returns:
            tuple: A tuple containing the URL of the uploaded file and a boolean indicating whether the upload was successful.
        """
        try:
            data = {"list": [local_file_path]}
            response = httpx.post(
                f"{self.endpoint}/upload",
                json=data,
                headers={"Content-Type": "application/json"},
            )
            result = response.json()

            if result.get("success"):
                return result["result"][0], True
            else:
                logging.error(
                    f"Failed to upload file: {local_file_path}, PicGO response: {result}"
                )
                return result, False

        except Exception as e:
            logging.exception(f"Error uploading file: {local_file_path}, {str(e)}")
            return str(e), False


def PicGO(endpoint="http://127.0.0.1:36677") -> callable:
    """Initialize the PicGO client and return a callable function to upload files.

    Args:
        endpoint (str): The endpoint for PicGO API. Defaults to "http://127.0.0.1:36677".

    Returns:
        callable: The upload_file method of the PicGO client.
    """
    picgo_uploader = PicGO_Settings(endpoint=endpoint)
    return picgo_uploader.upload_file
