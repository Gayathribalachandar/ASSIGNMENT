from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class CandidateSource:

    source_id: str

    source_name: str

    source_type: str

    filename: str

    observations: Dict[str, Any]

    parser_confidence: float = 1.0

    metadata: Dict[str, Any] = field(default_factory=dict)