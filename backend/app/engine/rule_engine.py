from typing import Dict, List


class RuleEngine:
    """
    Applies configurable business rules
    to the canonical candidate.
    """

    DEFAULT_RULES = {

        "minimum_experience": 0,

        "required_skills": [],

        "required_certifications": [],

        "required_degree": None,

        "allowed_locations": []

    }

    def evaluate(
        self,
        candidate,
        rules=None
    ):

        rules = rules or self.DEFAULT_RULES

        result = {

            "passed": True,

            "violations": []

        }

        # ----------------------------------------

        if (
            candidate.years_experience or 0
        ) < rules["minimum_experience"]:

            result["passed"] = False

            result["violations"].append({

                "rule": "minimum_experience",

                "expected": rules["minimum_experience"],

                "actual": candidate.years_experience

            })

        # ----------------------------------------

        skills = {

            s["name"].lower()

            for s in candidate.skills

        }

        for skill in rules["required_skills"]:

            if skill.lower() not in skills:

                result["passed"] = False

                result["violations"].append({

                    "rule": "required_skill",

                    "value": skill

                })

        # ----------------------------------------

        certs = {

            c["name"].lower()

            for c in candidate.certifications

        }

        for cert in rules["required_certifications"]:

            if cert.lower() not in certs:

                result["passed"] = False

                result["violations"].append({

                    "rule": "required_certification",

                    "value": cert

                })

        # ----------------------------------------

        return result