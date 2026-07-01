from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Candidate:

    candidate_id: str = ""

    full_name: str = ""

    emails: List[str] = field(default_factory=list)

    phones: List[str] = field(default_factory=list)

    location: Dict[str, Optional[str]] = field(default_factory=lambda: {
        "city": "",
        "region": "",
        "country": ""
    })

    headline: Optional[str] = None

    years_experience: Optional[float] = None

    skills: List[Dict[str, Any]] = field(default_factory=list)

    experience: List[Dict[str, Any]] = field(default_factory=list)

    education: List[Dict[str, Any]] = field(default_factory=list)

    links: Dict[str, Any] = field(default_factory=lambda: {
        "linkedin": None,
        "github": None,
        "portfolio": None,
        "other": []
    })

    certifications: List[Dict[str, Any]] = field(default_factory=list)

    projects: List[Dict[str, Any]] = field(default_factory=list)

    summary: Optional[str] = None

    overall_confidence: float = 0.0

    confidence: Dict[str, float] = field(default_factory=dict)

    provenance: Dict[str, List[str]] = field(default_factory=dict)

    conflicts: List[Dict[str, Any]] = field(default_factory=list)

    trust_score: float = 0.0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):

        return {
            "candidate_id": self.candidate_id,
            "full_name": self.full_name,
            "emails": self.emails,
            "phones": self.phones,
            "location": self.location,
            "headline": self.headline,
            "years_experience": self.years_experience,
            "skills": self.skills,
            "experience": self.experience,
            "education": self.education,
            "links": self.links,
            "certifications": self.certifications,
            "projects": self.projects,
            "summary": self.summary,
            "overall_confidence": self.overall_confidence,
            "confidence": self.confidence,
            "provenance": self.provenance,
            "conflicts": self.conflicts,
            "trust_score": self.trust_score,
            "metadata": self.metadata,
        }