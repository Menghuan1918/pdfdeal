from enum import Enum

class OutputFormat(str, Enum):
    DOCX = "docx"
    TXTS = "txts"
    LATEX = "latex"
    MD= "md"
    MD_DOLLAR = "md_dollar"

class OutputVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"

class RAG_OutputType(str, Enum):
    PDF = "pdf"
    MD = "md"