import re

from app.utils.logger import logger


class TextProcessor:
    """
    Cleans and normalizes extracted resume text.
    """

    @staticmethod
    def clean(text: str) -> str:

        logger.info("Cleaning extracted resume text.")

        if not text:
            return ""

        # Convert Windows/Mac line endings to Unix
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Replace tabs with spaces
        text = text.replace("\t", " ")

        # Remove repeated spaces
        text = re.sub(r"[ ]{2,}", " ", text)

        # Remove repeated blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove trailing spaces
        text = "\n".join(line.strip() for line in text.split("\n"))

        # Remove leading/trailing whitespace
        text = text.strip()

        logger.info("Resume text cleaned successfully.")

        return text