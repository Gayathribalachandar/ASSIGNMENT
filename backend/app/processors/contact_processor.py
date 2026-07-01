import re
from typing import Dict

import phonenumbers

from app.utils.logger import logger


class ContactProcessor:
    """
    Extracts candidate contact information from cleaned resume text.
    """

    EMAIL_PATTERN = re.compile(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    )

    LINKEDIN_PATTERN = re.compile(
        r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+",
        re.IGNORECASE,
    )

    GITHUB_PATTERN = re.compile(
        r"(https?://)?(www\.)?github\.com/[A-Za-z0-9_-]+",
        re.IGNORECASE,
    )

    PHONE_PATTERN = re.compile(
        r"(\+?\d[\d\s\-\(\)]{8,}\d)"
    )

    @classmethod
    def extract(cls, text: str) -> Dict:

        logger.info("Extracting contact information.")

        result = {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "location": None,
        }

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        # -----------------------------
        # Name (first non-empty line)
        # -----------------------------

        if lines:
            result["name"] = lines[0]

        # -----------------------------
        # Email
        # -----------------------------

        email = cls.EMAIL_PATTERN.search(text)

        if email:
            result["email"] = email.group()

        # -----------------------------
        # LinkedIn
        # -----------------------------

        linkedin = cls.LINKEDIN_PATTERN.search(text)

        if linkedin:
            result["linkedin"] = linkedin.group()

        # -----------------------------
        # GitHub
        # -----------------------------

        github = cls.GITHUB_PATTERN.search(text)

        if github:
            result["github"] = github.group()

        # -----------------------------
        # Phone
        # -----------------------------

        phone_match = cls.PHONE_PATTERN.search(text)

        if phone_match:

            raw_phone = phone_match.group()

            try:

                phone = phonenumbers.parse(
                    raw_phone,
                    "IN"
                )

                if phonenumbers.is_valid_number(phone):

                    result["phone"] = phonenumbers.format_number(
                        phone,
                        phonenumbers.PhoneNumberFormat.E164
                    )

            except Exception:
                pass

        # -----------------------------
        # Location
        # -----------------------------

        for line in lines:
            label_match = re.match(r"^\s*([A-Za-z ]+)\s*[:\-]\s*(.*)$", line)
            if label_match:
                key = label_match.group(1).strip().lower()
                value = label_match.group(2).strip()
                if key in ("location", "address", "city", "region", "country") and value:
                    result["location"] = value
                    break

        if not result["location"]:
            for line in lines[:10]:
                if not line or line == result["name"]:
                    continue
                if ":" in line:
                    continue
                if cls.EMAIL_PATTERN.search(line):
                    continue
                if cls.LINKEDIN_PATTERN.search(line):
                    continue
                if cls.GITHUB_PATTERN.search(line):
                    continue
                if cls.PHONE_PATTERN.search(line):
                    continue

                if re.search(r"\b(CAND[-_ ]?\d+|@|https?:|github\.com|linkedin\.com|experience|skills|education|summary|cgpa)\b", line, re.IGNORECASE):
                    continue
                if re.search(r"\d", line):
                    continue
                candidate_parts = [
                    p.strip()
                    for p in re.split(r"[|•\-–,]+", line)
                    if p.strip()
                ]
                for part in candidate_parts:
                    if len(part) < 3:
                        continue
                    if re.search(r"\b(CAND[-_ ]?\d+|@|https?:|github\.com|linkedin\.com|experience|skills|education|summary|cgpa)\b", part, re.IGNORECASE):
                        continue
                    result["location"] = part
                    break
                if result["location"]:
                    break

        logger.info("Contact extraction completed.")

        return result