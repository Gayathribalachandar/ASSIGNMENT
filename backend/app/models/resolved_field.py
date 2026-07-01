from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class ResolvedField:

    value: Any

    confidence: float

    agreed_sources: int

    total_sources: int

    provenance: List[str] = field(default_factory=list)

    conflict: bool = False