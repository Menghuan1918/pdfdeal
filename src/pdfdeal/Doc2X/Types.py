from enum import Enum


class OutputFormat(str, Enum):
    DOCX = "docx"
    TXTS = "txts"
    LATEX = "latex"
    MD = "md"
    MD_DOLLAR = "md_dollar"

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, must be one of {', '.join([m.value for m in cls])}"
        )


class OutputVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, must be one of {', '.join([m.value for m in cls])}"
        )


class RAG_OutputType(str, Enum):
    PDF = "pdf"
    MD = "md"
    TEXTS = "texts"

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, must be one of {', '.join([m.value for m in cls])}"
        )
