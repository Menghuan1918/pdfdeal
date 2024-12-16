from .uploaders import UploaderFactory
from .converter import convert_pdf_to_md

class MarkerPDF:
    """
    MarkerPDF class for handling PDF to Markdown conversion with various processing options.
    
    Args:
        input_dir (str): Directory containing PDF files to process
        output_dir (str): Directory where converted files will be saved
        uploader_config (dict, optional): Configuration for image uploader
            Example for AliOSS:
            {
                'type': 'alioss',
                'access_key_id': 'your_key_id',
                'access_key_secret': 'your_key_secret',
                'endpoint': 'your_endpoint',
                'bucket': 'your_bucket'
            }
            Example for PicGO:
            {
                'type': 'picgo',
                'endpoint': 'http://127.0.0.1:36677'
            }
        qps (int, optional): Maximum queries per second for image uploading. Defaults to 0 (no limit)
        threads (int, optional): Number of threads for image processing. Defaults to 5
        steps_to_run (list, optional): List of steps to run [1, 2, 3]. Defaults to None (all steps)
        process_each (bool, optional): Whether to process each file immediately. Defaults to False
    
    Usage:
        # 基本使用（无上传器）
        marker = MarkerPDF("input_folder", "output_folder")
        result = marker.convert()

        # 使用 AliOSS 上传器的完整配置
        marker = MarkerPDF(
            input_dir="input_folder",
            output_dir="output_folder",
            uploader_config={
                'type': 'alioss',
                'access_key_id': 'your_key_id',
                'access_key_secret': 'your_key_secret',
                'endpoint': 'your_endpoint',
                'bucket': 'your_bucket'
            },
            qps=2000, 提供对上传器API querys per second per thread的限制功能
            threads=10,
            steps_to_run=[1, 3],
            process_each=True
        )
        result = marker.convert()

        # 使用 PicGO 上传器
        marker = MarkerPDF(
            input_dir="input_folder",
            output_dir="output_folder",
            uploader_config={
                'type': 'picgo',
                'endpoint': 'http://127.0.0.1:36677'
            },
            process_each=True
        )
        result = marker.convert()
    """
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        uploader_config: dict = None,
        qps: int = 0,
        threads: int = 5,
        steps_to_run: list = None,
        process_each: bool = False
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.qps = qps
        self.threads = threads
        self.steps_to_run = steps_to_run
        self.process_each = process_each
        self.uploader = None

        # Initialize uploader if config is provided
        if uploader_config:
            uploader_type = uploader_config.pop('type')
            self.uploader = UploaderFactory.create_uploader(uploader_type, **uploader_config)

    def convert(self):
        """
        Execute the PDF to Markdown conversion with current settings.
        
        Returns:
            dict: Conversion results containing success status and file lists
        """
        return convert_pdf_to_md(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            process_each=self.process_each,
            uploader=self.uploader.upload if self.uploader else None,
            qps=self.qps,
            steps_to_run=self.steps_to_run,
            threads=self.threads
        )