from typing import Dict


class DecisionEngine:
    """
    Produces the final hiring recommendation.

    Possible outcomes:

    APPROVE
    REVIEW
    REJECT
    """

    HIGH_TRUST = 90
    MEDIUM_TRUST = 70

    def decide(self, candidate) -> Dict:

        trust = candidate.trust_score

        conflicts = len(candidate.conflicts or [])

        validation_errors = self._validation_errors(candidate)

        # -----------------------------------------
        # Reject
        # -----------------------------------------

        if validation_errors:

            return {
                "decision": "REJECT",
                "reason": "Required candidate information is missing.",
                "trust_score": trust,
                "critical_conflicts": conflicts
            }

        # -----------------------------------------
        # Approve
        # -----------------------------------------

        if trust >= self.HIGH_TRUST and conflicts == 0:

            return {
                "decision": "APPROVE",
                "reason": "High confidence with no conflicting information.",
                "trust_score": trust,
                "critical_conflicts": conflicts
            }

        # -----------------------------------------
        # Manual Review
        # -----------------------------------------

        if trust >= self.MEDIUM_TRUST:

            return {
                "decision": "REVIEW",
                "reason": "Candidate appears valid but requires manual verification.",
                "trust_score": trust,
                "critical_conflicts": conflicts
            }

        # -----------------------------------------
        # Reject
        # -----------------------------------------

        return {
            "decision": "REJECT",
            "reason": "Low confidence candidate profile.",
            "trust_score": trust,
            "critical_conflicts": conflicts
        }

    # -------------------------------------------------

    def _validation_errors(self, candidate):

        required = [

            candidate.full_name,

            candidate.emails,

            candidate.skills

        ]

        for value in required:

            if value in ("", None, [], {}):

                return True

        return False