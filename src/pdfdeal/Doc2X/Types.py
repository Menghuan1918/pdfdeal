from enum import Enum


class OutputFormat(str, Enum):
    DOCX = "docx"
    TXTS = "texts"
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


class Support_File_Type(str, Enum):
    PDF = "pdf"
    IMG = "img"

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, must be one of {', '.join([m.value for m in cls])}"
        )


class Translate_Model(str, Enum):
    DEEPSEEK = "deepseek"
    GLM = "glm4"

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, must be one of {', '.join([m.value for m in cls])}"
        )


class Translate_Language(str, Enum):
    EN = "en"
    ZH = "zh"
    JA = "ja"
    FR = "fr"
    RU = "ru"
    PT = "pt"
    ES = "es"
    DE = "de"
    KO = "ko"
    AR = "ar"

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, must be one of {', '.join([m.value for m in cls])}"
        )
