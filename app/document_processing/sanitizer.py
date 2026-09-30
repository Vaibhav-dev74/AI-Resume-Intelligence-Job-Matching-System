import re
import unicodedata


class TextSanitizer:
    LIGATURES = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "*",
        "\u25cf": "*",
        "\u25aa": "*",
        "\u2023": "*",
    }

    @classmethod
    def clean(cls, text: str) -> str:
        if not text:
            return ""

        text = unicodedata.normalize("NFKD", text)

        for lig, repl in cls.LIGATURES.items():
            text = text.replace(lig, repl)

        text = re.sub(r"\r\n|\r", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

        return text.strip()


text_sanitizer = TextSanitizer()
