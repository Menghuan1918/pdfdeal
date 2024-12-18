from pdfdeal.FileTools.Img.Ali_OSS import Ali_OSS
from pdfdeal.FileTools.Img.PicGO import PicGO

class UploaderFactory:
    @staticmethod
    def create_uploader(uploader_type: str, **kwargs):
        """
        创建上传器实例
        
        Args:
            uploader_type: 上传器类型 ('alioss' 或 'picgo')
            **kwargs: 上传器所需的参数
        """
        if uploader_type.lower() == 'alioss':
            required_params = ['access_key_id', 'access_key_secret', 'endpoint', 'bucket']
            for param in required_params:
                if param not in kwargs:
                    raise ValueError(f"AliOSS uploader requires {param}")
            
            return Ali_OSS(
                OSS_ACCESS_KEY_ID=kwargs['access_key_id'],
                OSS_ACCESS_KEY_SECRET=kwargs['access_key_secret'],
                Endpoint=kwargs['endpoint'],
                Bucket=kwargs['bucket']
            )
            
        elif uploader_type.lower() == 'picgo':
            endpoint = kwargs.get('endpoint', 'http://127.0.0.1:36677')
            return PicGO(endpoint=endpoint)
            
        else:
            raise ValueError(f"Unsupported uploader type: {uploader_type}")