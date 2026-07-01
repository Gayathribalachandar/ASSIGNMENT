from app.utils.canonicalizer import *

class NormalizationProcessor:

    @staticmethod
    def normalize(candidate):

        contact = candidate["contact"]

        profile = candidate["profile"]

        # ------------------------

        contact["name"] = normalize_name(
            contact.get("name")
        )

        contact["email"] = normalize_email(
            contact.get("email")
        )

        contact["phone"] = normalize_phone(
            contact.get("phone")
        )

        contact["linkedin"] = normalize_linkedin(
            contact.get("linkedin")
        )

        # ------------------------

        profile["skills"] = [
            normalize_skill(skill)
            for raw_skill in profile.get("skills", [])
            for skill in split_skills(raw_skill)
            if normalize_skill(skill)
        ]

        profile["certifications"] = [

            normalize_certification(cert)

            for cert in profile.get(
                "certifications",
                []
            )

        ]

        return candidate