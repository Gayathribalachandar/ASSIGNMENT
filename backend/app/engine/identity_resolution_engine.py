from collections import defaultdict
from typing import List

from app.models.source import CandidateSource
from app.utils.canonicalizer import (
    normalize_name,
    normalize_email,
    normalize_phone,
)


class IdentityResolutionEngine:
    """
    Groups uploaded files that belong to the same candidate.

    Matching priority:

    1. Email
    2. Phone
    3. Name + Experience
    4. Name only

    Different people remain in different groups.
    """

    def group_candidates(
        self,
        sources: List[CandidateSource],
    ) -> List[List[CandidateSource]]:

        groups = []

        for source in sources:

            matched = False

            for group in groups:

                if self._belongs_to_group(source, group):

                    group.append(source)

                    matched = True

                    break

            if not matched:
                groups.append([source])

        return groups

    #########################################################

    def _belongs_to_group(
        self,
        source: CandidateSource,
        group: List[CandidateSource],
    ) -> bool:

        for existing in group:

            score = self._identity_score(
                source,
                existing
            )

            if score >= 70:
                return True

        return False

    #########################################################

    def _identity_score(
        self,
        a: CandidateSource,
        b: CandidateSource,
    ) -> int:

        score = 0

        # ------------------------
        # EMAIL
        # ------------------------

        emails_a = {
            normalize_email(x)
            for x in a.observations.get("emails", [])
            if x
        }

        emails_b = {
            normalize_email(x)
            for x in b.observations.get("emails", [])
            if x
        }

        if emails_a & emails_b:
            score += 60

        # ------------------------
        # PHONE
        # ------------------------

        phones_a = {
            normalize_phone(x)
            for x in a.observations.get("phones", [])
            if x
        }

        phones_b = {
            normalize_phone(x)
            for x in b.observations.get("phones", [])
            if x
        }

        if phones_a & phones_b:
            score += 40

        # ------------------------
        # NAME
        # ------------------------

        name_a = normalize_name(
            a.observations.get("full_name", "")
        )

        name_b = normalize_name(
            b.observations.get("full_name", "")
        )

        if name_a and name_b:

            if name_a == name_b:
                score += 30

            elif (
                name_a.replace(" ", "")
                ==
                name_b.replace(" ", "")
            ):
                score += 25

        # ------------------------
        # EXPERIENCE
        # ------------------------

        exp_a = a.observations.get(
            "years_experience"
        )

        exp_b = b.observations.get(
            "years_experience"
        )

        if (
            exp_a is not None
            and exp_b is not None
        ):

            try:

                if abs(
                    float(exp_a) - float(exp_b)
                ) <= 1:

                    score += 10

            except Exception:
                pass

        return score