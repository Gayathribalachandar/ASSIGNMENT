import pandas as pd
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


class RecruiterCSVConnector:
    """
    Generic CSV connector.

    Supports recruiter exports, HRMS exports,
    ATS exports and similar tabular candidate files.
    """

    def extract(self, csv_path):

        df = pd.read_csv(csv_path)

        if df.empty:
            raise Exception("CSV contains no records.")

        row = df.iloc[0].fillna("")

        emails = split_skills(row.get("email", ""))
        phones = split_skills(row.get("phone", ""))
        skills = split_skills(row.get("skills", ""))

        observations = {

            "full_name": normalize_name(
                row.get("name", "")
                or row.get("full_name", "")
            ),

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

            "headline": row.get("headline", ""),

            "location": row.get("location", ""),

            "years_experience": parse_years_experience(
                row.get("years_experience") or row.get("experience_years")
            ),

            "skills": [
                normalize_skill(skill)
                for skill in skills
                if normalize_skill(skill)
            ],

            "experience": [],

            "education": [],

            "links": {}
        }

        return CandidateSource(

            source_id="",

            source_name="Recruiter CSV",

            source_type="csv",

            filename=str(csv_path),

            observations=observations,

            parser_confidence=0.95
        )

    def _split(self, value):

        if not value:
            return []

        return [
            x.strip()
            for x in str(value).split(",")
            if x.strip()
        ]