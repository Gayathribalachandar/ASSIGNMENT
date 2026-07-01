from typing import Dict, List


class ValidationEngine:
    """
    Performs business validation on the canonical candidate.

    Unlike SchemaValidator, this validates
    candidate quality rather than schema.
    """

    REQUIRED_FIELDS = [
        "full_name",
        "emails",
        "phones",
        "skills"
    ]

    def validate(self, candidate):

        errors = []
        warnings = []

        for field in self.REQUIRED_FIELDS:

            value = getattr(candidate, field, None)

            if value in ("", None, [], {}):

                errors.append(
                    f"{field} is missing."
                )

        if candidate.years_experience is None:

            warnings.append(
                "Years of experience unavailable."
            )

        if len(candidate.skills) < 3:

            warnings.append(
                "Very few skills detected."
            )

        if not candidate.experience:

            warnings.append(
                "Experience section missing."
            )

        if not candidate.education:

            warnings.append(
                "Education section missing."
            )

        return {

            "passed": len(errors) == 0,

            "errors": errors,

            "warnings": warnings

        }