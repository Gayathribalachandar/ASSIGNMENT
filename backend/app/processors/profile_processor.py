import re
from typing import Dict, List

from app.utils.logger import logger


class ProfileProcessor:
    """
    Extracts structured profile information from resume text.
    """

    SECTION_HEADERS = [
        "Professional Summary",
        "Skills",
        "Education",
        "Experience",
        "Projects?",
        "Certifications?",
        "Languages"
    ]

    @staticmethod
    def extract_section(text: str, section: str) -> str:

        headers = "|".join(ProfileProcessor.SECTION_HEADERS)

        pattern = (
            rf"{section}\s*(.*?)"
            rf"(?=\n(?:{headers})\b|$)"
        )

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

        return match.group(1).strip() if match else ""

    @classmethod
    def extract(cls, text: str) -> Dict:

        logger.info("Extracting profile information.")

        summary = cls.extract_section(
            text,
            "Professional Summary"
        )

        skills_text = cls.extract_section(
            text,
            "Skills"
        )

        certifications_text = cls.extract_section(
            text,
            "Certification[s]?"
        )

        languages_text = cls.extract_section(
            text,
            "Languages"
        )

        skills = [
            skill.strip()
            for skill in re.split(r"[;,\n|]+", skills_text)
            if skill.strip()
        ]

        if not skills:
            fallback_skills = re.findall(
                r"Skills\s*[:\-]\s*(.+)",
                text,
                flags=re.IGNORECASE
            )
            for block in fallback_skills:
                skills.extend([
                    skill.strip()
                    for skill in re.split(r"[;,\n|]+", block)
                    if skill.strip()
                ])

        skills = [
            skill
            for skill in skills
            if not re.search(r"\b(email|phone|experience|cgpa|candidate|name)\b", skill, re.IGNORECASE)
        ]

        certifications = [
            line.strip()
            for line in certifications_text.split("\n")
            if line.strip()
        ]

        languages = [
            line.strip()
            for line in re.split(r",|\n", languages_text)
            if line.strip()
        ]

        return {

            "summary": summary,

            "skills": skills,

            "certifications": certifications,

            "languages": languages

        }