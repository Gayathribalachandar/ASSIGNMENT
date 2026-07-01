from typing import List, Dict

from app.models.source import CandidateSource


class ProvenanceEngine:
    """
    Builds provenance information for every resolved field.

    Instead of just listing filenames, it stores:
    - selected value
    - every observed value
    - originating file
    - source type
    - parser confidence

    This data is intended for the expandable
    "Explain Trust Score" section.
    """

    def build(
        self,
        field_name: str,
        selected_value,
        sources: List[CandidateSource]
    ) -> Dict:

        provenance = {

            "field": field_name,

            "selected": selected_value,

            "sources": []

        }

        for source in sources:

            value = source.observations.get(field_name)

            provenance["sources"].append({

                "filename": source.filename,

                "source_type": source.source_type,

                "value": value,

                "parser_confidence": source.parser_confidence

            })

        return provenance

    # ---------------------------------------------------

    def build_all(
        self,
        candidate,
        sources: List[CandidateSource]
    ) -> Dict:

        result = {}

        candidate_dict = candidate.to_dict()

        for field, value in candidate_dict.items():

            if field in (
                "confidence",
                "provenance",
                "metadata",
                "trust_score",
                "conflicts"
            ):
                continue

            result[field] = self.build(
                field,
                value,
                sources
            )

        return result