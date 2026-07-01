from typing import Dict, Any, List

WEIGHTS = {
    "name": 0.15,
    "email": 0.10,
    "phone": 0.10,
    "skills": 0.25,
    "experience": 0.25,
    "education": 0.15
}


def normalize(value):
    """
    Normalize values for fair comparison
    """
    if value is None:
        return ""

    if isinstance(value, list):
        return sorted([str(v).strip().lower() for v in value])

    return str(value).strip().lower()


def compare_documents(resume: Dict[str, Any], ats: Dict[str, Any]):

    conflicts = []
    total_weight = 0.0
    earned_score = 0.0

    for field, weight in WEIGHTS.items():
        r_val = normalize(resume.get(field))
        a_val = normalize(ats.get(field))

        total_weight += weight

        # ✅ EXACT MATCH
        if r_val == a_val and r_val != "":
            earned_score += weight
            continue

        # ❌ CONFLICT ONLY IF NOT MATCHING
        if r_val != a_val:
            conflicts.append({
                "field": field,
                "resume_value": resume.get(field),
                "ats_value": ats.get(field),
                "match_type": "mismatch"
            })

            # partial scoring logic (integrity-based)
            if r_val and a_val:
                earned_score += weight * 0.3
            elif r_val or a_val:
                earned_score += weight * 0.1
            else:
                earned_score += 0

    confidence_score = round(earned_score / total_weight, 3) if total_weight else 0.0

    return {
        "conflicts": conflicts,
        "confidence_score": confidence_score
    }