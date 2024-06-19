import httpx
import asyncio
import json
import os
import zipfile
import time
import re
from .file_tools import texts_to_file
from typing import Tuple, Literal
from .Doc2X.Exception import RateLimit
from .Doc2X.Convert import (
    refresh_key,
    unzip,
    get_limit,
    uuid2file,
    upload_pdf,
    upload_img,
    uuid_status
)

class Doc2x:
    def __init__(self, apikey: str="") -> None:
        self.apikey = apikey
