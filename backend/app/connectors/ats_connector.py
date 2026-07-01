from pathlib import Path
import json
import re

from app.models.source import CandidateSource
from app.utils.canonicalizer import (
    normalize_name,
    normalize_email,
    normalize_phone,
    normalize_skill,
    split_skills,
    parse_years_experience
)


class ATSConnector:

    def _normalize_record(self, data):

        if isinstance(data, list):
            if not data:
                raise Exception("ATS JSON contains no candidate records.")
            data = data[0]

        if not isinstance(data, dict):
            raise Exception("ATS JSON must contain a candidate object.")

        emails = data.get("emails")
        if emails is None:
            emails = [data.get("email")] if data.get("email") else []
        elif not isinstance(emails, list):
            emails = [emails]

        phones = data.get("phones")
        if phones is None:
            phones = [data.get("phone")] if data.get("phone") else []
        elif not isinstance(phones, list):
            phones = [phones]

        skills = data.get("skills")
        if skills is None:
            skills = []

        return {
            "full_name": normalize_name(data.get("full_name") or data.get("name", "")),
            "emails": [
                normalize_email(email)
                for email in emails
                if normalize_email(email)
            ],
            "phones": [
                normalize_phone(phone)
                for phone in phones
                if normalize_phone(phone)
            ],
            "location": data.get("location") or data.get("address", ""),
            "headline": data.get("headline", ""),
            "years_experience": parse_years_experience(
                data.get("years_experience") or data.get("experience_years")
            ),
            "skills": [
                normalize_skill(skill)
                for skill in split_skills(skills)
                if normalize_skill(skill)
            ],
            "experience": data.get("experience", []),
            "education": data.get("education", []),
            "links": data.get("links", {}),
            "projects": data.get("projects", []),
            "certifications": data.get("certifications", []),
            "summary": data.get("summary", "")
        }

    def extract(self, json_path):

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        observations = self._normalize_record(data)

        return CandidateSource(

            source_id="",

            source_name="ATS JSON",

            source_type="ats_json",

            filename=Path(json_path).name,

            observations=observations,

            parser_confidence=0.98
        )