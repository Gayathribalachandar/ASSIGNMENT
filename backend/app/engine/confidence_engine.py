from typing import Any, Dict, List, Set


class ConfidenceEngine:
    """
    Calculates field-level confidence and an overall
    trust score using:
      - source reliability weights
      - agreement bonus
      - validation bonus
      - conflict / uncertainty penalties
    """

    SOURCE_WEIGHTS = {
        "resume": 0.90,
        "resume_text": 0.88,
        "recruiter_notes": 0.82,
        "ats_json": 0.80,
        "csv": 0.78,
        "recruiter_csv": 0.78,
    }

    AGREEMENT_BONUS = 0.05
    VALIDATION_BONUS = 0.05
    CONFLICT_PENALTY = 0.10
    INVALID_SOURCE_PENALTY = 0.15
    MISSING_CRITICAL_PENALTY = 0.20

    CRITICAL_FIELDS = {"full_name", "emails", "phones"}
    VALIDATED_FIELDS = {"emails", "phones"}
    SCORABLE_FIELDS = [
        "full_name",
        "emails",
        "phones",
        "location",
        "headline",
        "years_experience",
        "skills",
        "experience",
        "education",
        "links",
        "certifications",
        "projects",
        "summary",
    ]

    def score_field(
        self,
        field_name: str,
        candidate: Any,
        sources: List[Any],
        conflict_fields: Set[str],
        uncertain_fields: Set[str],
        invalid_fields: Set[str],
    ) -> float:
        value = getattr(candidate, field_name, None)
        if not self._is_present(value):
            return 0.0

        source_types = self._source_types_for_field(candidate, field_name)
        if not source_types:
            return 0.0

        base = max(
            self.SOURCE_WEIGHTS.get(source_type, 0.75)
            for source_type in source_types
        )

        if len(source_types) > 1 and field_name not in conflict_fields:
            base += self.AGREEMENT_BONUS

        if field_name in self.VALIDATED_FIELDS and self._value_validated(
            field_name,
            value,
        ):
            base += self.VALIDATION_BONUS

        if field_name in conflict_fields:
            base -= self.CONFLICT_PENALTY

        if field_name in uncertain_fields or field_name in invalid_fields:
            base -= self.INVALID_SOURCE_PENALTY

        return round(max(0.0, min(1.0, base)), 2)

    def score_profile(
        self,
        candidate: Any,
        sources: List[Any],
    ) -> Dict[str, float]:
        conflict_fields = {
            entry["field"]
            for entry in getattr(candidate, "conflicts", [])
            if isinstance(entry, dict) and "field" in entry
        }
        uncertain_fields = self._collect_uncertain_fields(sources)
        invalid_fields = self._collect_invalid_fields(sources)

        scores: Dict[str, float] = {}
        for field in self.SCORABLE_FIELDS:
            scores[field] = self.score_field(
                field,
                candidate,
                sources,
                conflict_fields,
                uncertain_fields,
                invalid_fields,
            )

        for field in self.CRITICAL_FIELDS:
            if not self._is_present(getattr(candidate, field, None)):
                scores[field] = round(
                    max(0.0, scores.get(field, 0.0) - self.MISSING_CRITICAL_PENALTY),
                    2,
                )

        return scores

    def overall(self, confidence: Dict[str, float]) -> float:

        if not confidence:
            return 0.0

        return round(
            (sum(confidence.values()) / len(confidence)) * 100,
            2
        )

    def _source_types_for_field(self, candidate: Any, field_name: str) -> Set[str]:
        provenance = getattr(candidate, "provenance", {}).get(field_name, {})
        sources = provenance.get("sources", []) if isinstance(provenance, dict) else []
        types: Set[str] = set()

        for source in sources:
            if isinstance(source, dict):
                source_type = source.get("source_type")
                if source_type:
                    types.add(source_type)
            elif isinstance(source, str):
                types.add(source)

        return types

    def _collect_uncertain_fields(self, sources: List[Any]) -> Set[str]:
        fields: Set[str] = set()
        for src in sources:
            metadata = getattr(src, "metadata", {})
            if isinstance(metadata, dict):
                fields.update(metadata.get("_uncertain_fields", []))
        return fields

    def _collect_invalid_fields(self, sources: List[Any]) -> Set[str]:
        fields: Set[str] = set()
        for src in sources:
            metadata = getattr(src, "metadata", {})
            if isinstance(metadata, dict):
                fields.update(metadata.get("_invalid_fields", []))
        return fields

    @staticmethod
    def _value_validated(field_name: str, value: Any) -> bool:
        if field_name == "phones":
            return isinstance(value, list) and all(
                isinstance(phone, str) and phone.startswith("+") for phone in value
            )
        if field_name == "emails":
            return isinstance(value, list) and all(
                isinstance(email, str) and "@" in email for email in value
            )
        return False

    @staticmethod
    def _is_present(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, (list, dict, str)) and not value:
            return False
        return True
