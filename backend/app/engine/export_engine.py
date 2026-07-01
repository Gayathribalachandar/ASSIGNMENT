import csv
import json
from io import StringIO
from typing import Dict, Any


class ExportEngine:
    """
    Export canonical candidate into multiple formats.

    Supported:
        - JSON
        - CSV
        - ATS JSON
    """

    def export(
        self,
        candidate,
        format: str = "json"
    ):

        format = format.lower()

        if format == "json":
            return self._export_json(candidate)

        if format == "csv":
            return self._export_csv(candidate)

        if format == "ats":
            return self._export_ats(candidate)

        raise ValueError(f"Unsupported export format: {format}")

    # -----------------------------------------------------

    def _export_json(self, candidate):

        return json.dumps(
            candidate.to_dict(),
            indent=4,
            default=str
        )

    # -----------------------------------------------------

    def _export_csv(self, candidate):

        output = StringIO()

        writer = csv.writer(output)

        writer.writerow([
            "Candidate ID",
            "Full Name",
            "Emails",
            "Phones",
            "Experience",
            "Skills",
            "Trust Score"
        ])

        writer.writerow([

            candidate.candidate_id,

            candidate.full_name,

            ", ".join(candidate.emails),

            ", ".join(candidate.phones),

            candidate.years_experience,

            ", ".join(
                [
                    skill["name"]
                    if isinstance(skill, dict)
                    else str(skill)
                    for skill in candidate.skills
                ]
            ),

            candidate.trust_score

        ])

        return output.getvalue()

    # -----------------------------------------------------

    def _export_ats(self, candidate):

        return {

            "candidateId": candidate.candidate_id,

            "name": candidate.full_name,

            "emails": candidate.emails,

            "phones": candidate.phones,

            "headline": candidate.headline,

            "summary": candidate.summary,

            "experienceYears": candidate.years_experience,

            "skills": [
                skill["name"]
                if isinstance(skill, dict)
                else skill
                for skill in candidate.skills
            ],

            "education": candidate.education,

            "experience": candidate.experience,

            "projects": candidate.projects,

            "certifications": candidate.certifications,

            "links": candidate.links,

            "trustScore": candidate.trust_score

        }