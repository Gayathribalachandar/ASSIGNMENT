import re
from typing import Dict, List

from app.utils.logger import logger


class ExperienceProcessor:

    @staticmethod
    def _extract(text: str, start: str, end: str = None):

        if end:

            pattern = rf"{start}\s*(.*?)(?=\n{end}|$)"

        else:

            pattern = rf"{start}\s*(.*)"

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        return match.group(1).strip() if match else ""

    @classmethod
    def extract(cls, text: str) -> Dict:

        logger.info("Extracting education, experience and projects.")

        education = cls._extract(
            text,
            "Education",
            "Experience"
        )

        experience = cls._extract(
            text,
            "Experience",
            "Project"
        )

        projects = cls._extract(
            text,
            "Project[s]?",
            "Certification"
        )

        def parse_lines(section_text: str) -> List[str]:
            return [
                line.strip("•-* ")
                for line in section_text.split("\n")
                if line.strip()
            ]

        return {

            "education": [
                {"institution": line, "degree": None, "field": None, "end_year": None}
                for line in parse_lines(education)
            ],

            "experience": [
                {"company": None, "title": None, "start": None, "end": None, "summary": line}
                for line in parse_lines(experience)
            ],

            "projects": [
                {"name": None, "summary": line}
                for line in parse_lines(projects)
            ]

        }