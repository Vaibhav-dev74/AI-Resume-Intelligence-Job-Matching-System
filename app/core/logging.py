import logging
import re
import sys
from typing import Any


class PIIMaskingFilter(logging.Filter):
    EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
    PHONE_REGEX = re.compile(r"(\+?[0-9]{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)(\d{3}[-.\s]?\d{4})")

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.mask_text(record.msg)
        return True

    @classmethod
    def mask_text(cls, text: str) -> str:
        def email_repl(match):
            name, domain = match.group(1), match.group(2)
            if len(name) <= 2:
                masked_name = name[0] + "*"
            else:
                masked_name = name[0] + "***" + name[-1]
            return f"{masked_name}@{domain}"

        text = cls.EMAIL_REGEX.sub(email_repl, text)
        text = cls.PHONE_REGEX.sub(r"***-***-\3", text)
        return text


def setup_logger(name: str = "ai_resume_platform") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.addFilter(PIIMaskingFilter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = setup_logger()
