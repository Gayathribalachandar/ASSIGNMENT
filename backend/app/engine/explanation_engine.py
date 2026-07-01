from typing import Any, Dict


class ExplanationEngine:
    """
    Generates field-level explanations for the frontend.

    Each field contains:
    - confidence
    - selected value
    - provenance
    - conflict information
    """

    def build(self, candidate) -> Dict[str, Any]:

        explanation = {}

        confidence = candidate.confidence or {}
        provenance = candidate.provenance or {}
        conflicts = candidate.conflicts or []

        conflict_map = {}

        for conflict in conflicts:
            field = conflict.get("field")
            if field:
                conflict_map[field] = conflict

        fields = set()

        fields.update(confidence.keys())
        fields.update(provenance.keys())
        fields.update(conflict_map.keys())

        for field in sorted(fields):

            prov = provenance.get(field, {})

            explanation[field] = {
                "confidence": confidence.get(field, 0),
                "selected": prov.get("selected"),
                "sources": prov.get("sources", []),
                "has_conflict": field in conflict_map,
                "conflict": conflict_map.get(field)
            }

        return explanation

    def build_summary(self, candidate) -> Dict[str, Any]:

        confidence = candidate.confidence or {}

        total_fields = len(confidence)

        resolved_fields = sum(
            1 for value in confidence.values() if value > 0
        )

        conflict_count = len(candidate.conflicts or [])

        return {
            "candidate_id": candidate.candidate_id,
            "trust_score": candidate.trust_score,
            "resolved_fields": resolved_fields,
            "total_fields": total_fields,
            "conflict_count": conflict_count,
            "fields": self.build(candidate)
        }