from datetime import datetime
from typing import Dict, List


class AuditEngine:
    """
    Maintains an audit trail of every decision taken
    during candidate resolution.
    """

    def build(self, candidate) -> Dict:

        return {

            "candidate_id": candidate.candidate_id,

            "generated_at": datetime.utcnow().isoformat(),

            "trust_score": candidate.trust_score,

            "field_count": len(candidate.confidence),

            "conflict_count": len(candidate.conflicts),

            "events": self._build_events(candidate)

        }

    # ---------------------------------------------------------

    def _build_events(self, candidate) -> List[Dict]:

        events = []

        provenance = candidate.provenance or {}

        confidence = candidate.confidence or {}

        conflict_lookup = {

            c["field"]: c

            for c in candidate.conflicts

        }

        for field, info in provenance.items():

            events.append({

                "field": field,

                "selected_value": info.get("selected"),

                "confidence": confidence.get(field, 0),

                "sources": info.get("sources", []),

                "conflict": conflict_lookup.get(field)

            })

        return events