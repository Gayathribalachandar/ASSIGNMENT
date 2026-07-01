from collections import Counter
from typing import List
from uuid import uuid4

from app.engine.confidence_engine import ConfidenceEngine
from app.models.candidate import Candidate
from app.models.source import CandidateSource

from app.utils.canonicalizer import (
    normalize_email,
    normalize_phone,
    normalize_skill,
    normalize_linkedin,
    normalize_github,
    normalize_text,
    normalize_name,
    parse_years_experience,
)


class ResolutionEngine:
    """
    Multi-source candidate resolution engine.

    Combines multiple CandidateSource objects into a single
    canonical Candidate profile.
    """

    def __init__(self):
        self._confidence_engine = ConfidenceEngine()

    # ============================================================
    # PUBLIC API
    # ============================================================

    def resolve(
        self,
        sources: List[CandidateSource]
    ) -> Candidate:

        candidate = Candidate()
        candidate.candidate_id = str(uuid4())

        candidate.full_name = self._resolve_scalar(
            sources,
            "full_name",
            candidate,
            normalize_name
        )

        candidate.emails = self._resolve_list(
            sources,
            "emails",
            candidate,
            normalize_email
        )

        candidate.phones = self._resolve_list(
            sources,
            "phones",
            candidate,
            normalize_phone
        )

        candidate.location = self._resolve_location(
            sources,
            candidate
        )

        candidate.headline = self._resolve_scalar(
            sources,
            "headline",
            candidate,
            normalize_text
        )

        candidate.summary = self._resolve_summary(
            sources,
            candidate
        )

        candidate.years_experience = self._resolve_numeric(
            sources,
            "years_experience",
            candidate
        )

        candidate.skills = self._resolve_skills(
            sources,
            candidate
        )

        candidate.experience = self._resolve_experience(
            sources,
            candidate
        )

        candidate.education = self._resolve_education(
            sources,
            candidate
        )

        candidate.projects = self._merge_objects(
            sources,
            "projects"
        )

        candidate.certifications = self._resolve_certifications(
            sources,
            candidate
        )

        candidate.links = self._merge_dictionary(
            sources,
            "links"
        )

        self._finalize_candidate(candidate)

        candidate.confidence = self._confidence_engine.score_profile(
            candidate,
            sources
        )

        candidate.trust_score = self._calculate_trust(candidate)

        return candidate

    # ============================================================
    # GENERIC SCALAR RESOLVER
    # ============================================================

    def _resolve_scalar(
        self,
        sources,
        field,
        candidate,
        normalizer=lambda x: x
    ):

        buckets = {}
        provenance = []

        for src in sources:

            value = src.observations.get(field)

            if value in ("", None):
                continue

            normalized = normalizer(value)

            if not normalized:
                continue

            key = str(normalized).strip().lower()

            if key not in buckets:

                buckets[key] = {
                    "value": normalized,
                    "count": 0,
                    "sources": []
                }

            buckets[key]["count"] += 1

            buckets[key]["sources"].append({
                "filename": src.filename,
                "source_type": src.source_type,
                "confidence": src.parser_confidence,
                "value": value
            })

            provenance.append({
                "filename": src.filename,
                "source_type": src.source_type,
                "confidence": src.parser_confidence,
                "value": value
            })

        if not buckets:

            candidate.confidence[field] = 0

            candidate.provenance[field] = {
                "selected": None,
                "sources": []
            }

            return None

        winner = max(
            buckets.values(),
            key=lambda x: (
                x["count"],
                max(
                    s["confidence"]
                    for s in x["sources"]
                )
            )
        )

        confidence = round(
            winner["count"] /
            max(len(sources), 1),
            2
        )

        candidate.confidence[field] = confidence

        candidate.provenance[field] = {
            "selected": winner["value"],
            "sources": provenance
        }

        if len(buckets) > 1:

            candidate.conflicts.append({
                "field": field,
                "selected": winner["value"],
                "observed": [
                    b["value"]
                    for b in buckets.values()
                ]
            })

        return winner["value"]

    # ============================================================
    # GENERIC LIST RESOLVER
    # ============================================================

    def _resolve_list(
        self,
        sources,
        field,
        candidate,
        normalizer=lambda x: x
    ):

        unique = {}
        provenance = []

        for src in sources:

            values = src.observations.get(field, [])

            if not isinstance(values, list):
                values = [values]

            for value in values:

                normalized = normalizer(value)

                if not normalized:
                    continue

                key = normalized.lower()

                if key not in unique:
                    unique[key] = normalized

            provenance.append({
                "filename": src.filename,
                "source_type": src.source_type,
                "confidence": src.parser_confidence,
                "value": values
            })

        result = list(unique.values())

        candidate.confidence[field] = (
            1.0 if result else 0.0
        )

        candidate.provenance[field] = {
            "selected": result,
            "sources": provenance
        }

        return result

    # ============================================================
    # NUMERIC RESOLVER
    # ============================================================

    def _resolve_numeric(
        self,
        sources,
        field,
        candidate
    ):

        values = []
        provenance = []

        for src in sources:

            value = src.observations.get(field)

            if value in ("", None):
                continue

            try:
                value = float(value)
            except Exception:
                continue

            values.append(value)

            provenance.append({
                "filename": src.filename,
                "source_type": src.source_type,
                "confidence": src.parser_confidence,
                "value": value
            })

        if not values:

            candidate.confidence[field] = 0

            candidate.provenance[field] = {
                "selected": None,
                "sources": []
            }

            return None

        selected = max(values)

        candidate.confidence[field] = 1.0

        candidate.provenance[field] = {
            "selected": selected,
            "sources": provenance
        }

        return selected
        # ============================================================
    # LOCATION RESOLVER
    # ============================================================

    def _resolve_location(
        self,
        sources: List[CandidateSource],
        candidate: Candidate
    ):

        values = []
        provenance = []

        for src in sources:

            location = src.observations.get("location")

            if not location:
                continue

            if isinstance(location, dict):

                city = normalize_text(location.get("city", ""))
                region = normalize_text(location.get("region", ""))
                country = normalize_text(location.get("country", ""))

                location_string = ", ".join(
                    x for x in [city, region, country] if x
                )

            else:

                location_string = normalize_text(str(location))

            if not location_string:
                continue

            values.append(location_string)

            provenance.append({
                "filename": src.filename,
                "source_type": src.source_type,
                "confidence": src.parser_confidence,
                "value": location_string
            })

        if not values:

            candidate.confidence["location"] = 0.0

            candidate.provenance["location"] = {
                "selected": None,
                "sources": []
            }

            return {
                "city": None,
                "region": None,
                "country": None
            }

        winner, count = Counter(values).most_common(1)[0]

        confidence = round(
            count / max(len(values), 1),
            2
        )

        candidate.confidence["location"] = confidence

        candidate.provenance["location"] = {
            "selected": winner,
            "sources": provenance
        }

        if len(set(values)) > 1:

            candidate.conflicts.append({
                "field": "location",
                "selected": winner,
                "observed": values
            })

        parts = [x.strip() for x in winner.split(",") if x.strip()]

        return {
            "city": parts[0] if len(parts) > 0 else None,
            "region": parts[1] if len(parts) > 1 else None,
            "country": parts[2] if len(parts) > 2 else None
        }
        # ============================================================
    # SKILLS RESOLVER
    # ============================================================

    def _resolve_skills(
        self,
        sources: List[CandidateSource],
        candidate: Candidate
    ):

        skill_map = {}

        total_sources = max(len(sources), 1)

        for src in sources:

            skills = src.observations.get("skills", [])

            if not isinstance(skills, list):
                skills = [skills]

            for skill in skills:

                name = normalize_skill(skill)

                if not name:
                    continue

                key = name.lower()

                if key not in skill_map:

                    skill_map[key] = {
                        "name": name,
                        "count": 0,
                        "sources": []
                    }

                skill_map[key]["count"] += 1

                skill_map[key]["sources"].append({
                    "filename": src.filename,
                    "source_type": src.source_type,
                    "confidence": src.parser_confidence
                })

        result = []

        for skill in skill_map.values():

            confidence = round(
                skill["count"] / total_sources,
                2
            )

            result.append({
                "name": skill["name"],
                "confidence": confidence,
                "sources": skill["sources"]
            })

        result.sort(
            key=lambda x: (
                -x["confidence"],
                x["name"]
            )
        )

        candidate.confidence["skills"] = (
            1.0 if result else 0.0
        )

        candidate.provenance["skills"] = {
            "selected": [
                s["name"]
                for s in result
            ],
            "sources": [
                {
                    "filename": src.filename,
                    "source_type": src.source_type
                }
                for src in sources
            ]
        }

        return result
        # ============================================================
    # EXPERIENCE RESOLVER
    # ============================================================

    def _resolve_experience(
        self,
        sources: List[CandidateSource],
        candidate: Candidate
    ):

        jobs = {}
        provenance = []

        for src in sources:

            experiences = src.observations.get(
                "experience",
                []
            )

            if not isinstance(experiences, list):
                experiences = [experiences]

            for exp in experiences:

                if not isinstance(exp, dict):
                    continue

                company = normalize_text(
                    exp.get("company")
                    or exp.get("employer", "")
                )

                title = normalize_text(
                    exp.get("title")
                    or exp.get("designation", "")
                )

                key = f"{company.lower()}|{title.lower()}"

                if key not in jobs:

                    jobs[key] = {

                        "company": company,

                        "title": title,

                        "start": exp.get("start")
                            or exp.get("start_date"),

                        "end": exp.get("end")
                            or exp.get("end_date"),

                        "summary": exp.get("summary")
                            or exp.get("description", ""),

                        "sources": []

                    }

                else:

                    existing = jobs[key]

                    if not existing["summary"]:
                        existing["summary"] = (
                            exp.get("summary")
                            or exp.get("description", "")
                        )

                    if not existing["start"]:
                        existing["start"] = (
                            exp.get("start")
                            or exp.get("start_date")
                        )

                    if not existing["end"]:
                        existing["end"] = (
                            exp.get("end")
                            or exp.get("end_date")
                        )

                jobs[key]["sources"].append({

                    "filename": src.filename,

                    "source_type": src.source_type,

                    "confidence": src.parser_confidence

                })

            provenance.append({

                "filename": src.filename,

                "source_type": src.source_type

            })

        result = list(jobs.values())

        candidate.confidence["experience"] = (
            1.0 if result else 0.0
        )

        candidate.provenance["experience"] = {

            "selected": result,

            "sources": provenance

        }

        return result
        # ============================================================
    # EDUCATION RESOLVER
    # ============================================================

    def _resolve_education(
        self,
        sources: List[CandidateSource],
        candidate: Candidate
    ):

        schools = {}
        provenance = []

        for src in sources:

            education = src.observations.get(
                "education",
                []
            )

            if not isinstance(education, list):
                education = [education]

            for edu in education:

                if not isinstance(edu, dict):
                    continue

                institution = normalize_text(
                    edu.get("institution")
                    or edu.get("school", "")
                )

                degree = normalize_text(
                    edu.get("degree", "")
                )

                field = normalize_text(
                    edu.get("field")
                    or edu.get("branch", "")
                )

                end_year = (
                    edu.get("end_year")
                    or edu.get("graduation_year")
                    or edu.get("year")
                )

                key = (
                    f"{institution.lower()}|"
                    f"{degree.lower()}|"
                    f"{field.lower()}"
                )

                if key not in schools:

                    schools[key] = {

                        "institution": institution,

                        "degree": degree,

                        "field": field,

                        "end_year": end_year,

                        "sources": []

                    }

                else:

                    existing = schools[key]

                    if not existing["end_year"]:
                        existing["end_year"] = end_year

                schools[key]["sources"].append({

                    "filename": src.filename,

                    "source_type": src.source_type,

                    "confidence": src.parser_confidence

                })

            provenance.append({

                "filename": src.filename,

                "source_type": src.source_type

            })

        result = list(schools.values())

        candidate.confidence["education"] = (
            1.0 if result else 0.0
        )

        candidate.provenance["education"] = {

            "selected": result,

            "sources": provenance

        }

        return result
        # ============================================================
    # CERTIFICATIONS RESOLVER
    # ============================================================

    def _resolve_certifications(
        self,
        sources: List[CandidateSource],
        candidate: Candidate
    ):

        certifications = {}
        provenance = []

        for src in sources:

            values = src.observations.get(
                "certifications",
                []
            )

            if not isinstance(values, list):
                values = [values]

            for cert in values:

                if isinstance(cert, str):

                    cert = {
                        "name": cert
                    }

                if not isinstance(cert, dict):
                    continue

                name = normalize_text(
                    cert.get("name")
                    or cert.get("certification", "")
                )

                if not name:
                    continue

                key = name.lower()

                if key not in certifications:

                    certifications[key] = {

                        "name": name,

                        "issuer": cert.get("issuer")
                            or cert.get("organization"),

                        "year": cert.get("year")
                            or cert.get("issued_year"),

                        "sources": []

                    }

                else:

                    existing = certifications[key]

                    if not existing["issuer"]:
                        existing["issuer"] = (
                            cert.get("issuer")
                            or cert.get("organization")
                        )

                    if not existing["year"]:
                        existing["year"] = (
                            cert.get("year")
                            or cert.get("issued_year")
                        )

                certifications[key]["sources"].append({

                    "filename": src.filename,

                    "source_type": src.source_type,

                    "confidence": src.parser_confidence

                })

            provenance.append({

                "filename": src.filename,

                "source_type": src.source_type

            })

        result = list(certifications.values())

        candidate.confidence["certifications"] = (
            1.0 if result else 0.0
        )

        candidate.provenance["certifications"] = {

            "selected": [
                cert["name"]
                for cert in result
            ],

            "sources": provenance

        }

        return result
        # ============================================================
    # MERGE DICTIONARY
    # ============================================================

    def _merge_dictionary(
        self,
        sources: List[CandidateSource],
        field: str
    ):

        merged = {}

        for src in sources:

            value = src.observations.get(field)

            if not isinstance(value, dict):
                continue

            for key, val in value.items():

                if val in ("", None):
                    continue

                if key not in merged:

                    merged[key] = val

                else:

                    if not merged[key]:
                        merged[key] = val

        return merged
        # ============================================================
    # MERGE LIST OF OBJECTS
    # ============================================================

    def _merge_objects(
        self,
        sources: List[CandidateSource],
        field: str
    ):

        merged = []
        seen = set()

        for src in sources:

            values = src.observations.get(field, [])

            if not isinstance(values, list):
                values = [values]

            for obj in values:

                if isinstance(obj, dict):

                    key = (
                        obj.get("name")
                        or obj.get("title")
                        or obj.get("project_name")
                        or str(obj)
                    ).strip().lower()

                else:

                    key = str(obj).strip().lower()

                if key in seen:
                    continue

                seen.add(key)

                merged.append(obj)

        return merged
        # ============================================================
    # NORMALIZE & REMOVE DUPLICATES
    # ============================================================

    def _normalize_unique_list(
        self,
        values,
        normalizer
    ):

        unique = []
        seen = set()

        for value in values:

            normalized = normalizer(value)

            if not normalized:
                continue

            key = str(normalized).strip().lower()

            if key in seen:
                continue

            seen.add(key)

            unique.append(normalized)

        return unique
        # ============================================================
    # FINAL CLEANUP
    # ============================================================

    def _finalize_candidate(
        self,
        candidate: Candidate
    ):

        # ------------------------
        # Normalize Emails
        # ------------------------

        candidate.emails = self._normalize_unique_list(
            candidate.emails,
            normalize_email
        )

        # ------------------------
        # Normalize Phones
        # ------------------------

        candidate.phones = self._normalize_unique_list(
            candidate.phones,
            normalize_phone
        )

        # ------------------------
        # Normalize Experience
        # ------------------------

        candidate.years_experience = parse_years_experience(
            candidate.years_experience
        )

        # ------------------------
        # Normalize Skills
        # ------------------------

        if candidate.skills:

            unique_skills = {}
            normalized_skills = []

            for skill in candidate.skills:

                if isinstance(skill, dict):

                    name = normalize_skill(
                        skill.get("name")
                    )

                    if not name:
                        continue

                    key = name.lower()

                    if key in unique_skills:
                        continue

                    unique_skills[key] = True

                    skill["name"] = name

                    normalized_skills.append(skill)

            candidate.skills = normalized_skills

        # ------------------------
        # Normalize Links
        # ------------------------

        if candidate.links:

            if candidate.links.get("linkedin"):

                candidate.links["linkedin"] = normalize_linkedin(
                    candidate.links["linkedin"]
                )

            if candidate.links.get("github"):

                candidate.links["github"] = normalize_github(
                    candidate.links["github"]
                )

        # ------------------------
        # Normalize Location
        # ------------------------

        if candidate.location:

            candidate.location = {

                "city": normalize_text(
                    candidate.location.get("city")
                ),

                "region": normalize_text(
                    candidate.location.get("region")
                ),

                "country": normalize_text(
                    candidate.location.get("country")
                )

            }

        # ------------------------
        # Normalize Name
        # ------------------------

        if candidate.full_name:

            candidate.full_name = normalize_name(
                candidate.full_name
            )

        # ------------------------
        # Normalize Headline
        # ------------------------

        if candidate.headline:

            candidate.headline = normalize_text(
                candidate.headline
            )

        # ------------------------
        # Normalize Summary
        # ------------------------

        if candidate.summary:

            candidate.summary = " ".join(
                candidate.summary.split()
            )
            # ============================================================
    # SUMMARY RESOLVER
    # ============================================================

    def _resolve_summary(
        self,
        sources: List[CandidateSource],
        candidate: Candidate
    ):

        summary = self._resolve_scalar(
            sources,
            "summary",
            candidate,
            normalize_text
        )

        if not summary:
            return None

        summary = " ".join(summary.split())

        candidate.confidence["summary"] = (
            candidate.confidence.get("summary", 1.0)
        )

        return summary
        # ============================================================
    # OVERALL TRUST SCORE
    # ============================================================

    def _calculate_trust(
        self,
        candidate: Candidate
    ) -> float:

        weights = {

            "full_name": 10,

            "emails": 10,

            "phones": 10,

            "location": 5,

            "headline": 5,

            "summary": 5,

            "years_experience": 8,

            "skills": 20,

            "experience": 15,

            "education": 10,

            "projects": 5,

            "certifications": 2

        }

        total_weight = sum(weights.values())

        if total_weight == 0:
            return 0.0

        score = 0.0

        for field, weight in weights.items():

            confidence = candidate.confidence.get(field, 0.0)

            score += confidence * weight

        return round(
            (score / total_weight) * 100,
            2
        )