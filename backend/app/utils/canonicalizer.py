import re
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from dateutil import parser as date_parser

SKILL_MAP = {
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "node": "Node.js",
    "nodejs": "Node.js",
    "fast api": "FastAPI",
    "fastapi": "FastAPI",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "sql": "SQL",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning"
}

COUNTRY_MAP = {
    "india": "IN",
    "ind": "IN",
    "in": "IN",
    "united states": "US",
    "usa": "US",
    "us": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "great britain": "GB",
    "canada": "CA",
    "can": "CA",
    "ca": "CA",
    "australia": "AU",
    "aus": "AU",
    "au": "AU",
    "germany": "DE",
    "de": "DE",
    "france": "FR",
    "fr": "FR"
}

def normalize_text(value):
    if not value:
        return ""
    return str(value).strip()

NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20
}


def split_values(value, separators=r"[;,\n|]+"):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        values = []
        for item in value:
            values.extend(split_values(item, separators=separators))
        return [str(v).strip() for v in values if str(v).strip()]
    if isinstance(value, dict):
        return []
    text = str(value)
    return [item.strip() for item in re.split(separators, text) if item.strip()]


def split_skills(skills):
    return split_values(skills)


def parse_years_experience(value):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    text = text.lower()
    # Direct numeric parse
    number_match = re.search(r"(\d+(?:\.\d+)?)", text)
    if number_match:
        try:
            return float(number_match.group(1))
        except ValueError:
            pass
    # Word-based numbers
    tokens = re.findall(r"[a-z]+", text)
    for token in tokens:
        if token in NUMBER_WORDS:
            return float(NUMBER_WORDS[token])
    return None

def normalize_name(name):
    if not name:
        return None
    name = str(name).strip()
    # Remove candidate ids and similar metadata in parentheses
    name = re.sub(r"\s*\(CAND[-_ ]?\d+\)", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s*CAND[-_ ]?\d+\b", "", name, flags=re.IGNORECASE)
    # Add whitespace between camelcase words like JohnDoe -> John Doe
    name = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name)
    # Normalize multiple whitespace characters
    name = re.sub(r"\s+", " ", name)
    return name.title()

def normalize_email(email):
    if not email:
        return None
    try:
        normalized = validate_email(
            email,
            check_deliverability=False
        ).normalized
        return normalized.lower()
    except EmailNotValidError:
        return email.lower().strip()

def normalize_phone(phone):
    if not phone:
        return None
    try:
        # Try cleaning the string first
        cleaned = re.sub(r"[^\d+]", "", phone)
        # Parse
        parsed = phonenumbers.parse(phone, "IN")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )
    except:
        pass
    
    # Simple fallback: keep digits and optional +
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 10:
        if phone.startswith("+"):
            return f"+{digits}"
        # If it doesn't start with +, but has 10 digits and is in IN, default +91
        if len(digits) == 10:
            return f"+91{digits}"
        elif len(digits) == 12 and digits.startswith("91"):
            return f"+{digits}"
        return f"+{digits}"
    return None

def normalize_linkedin(url):
    if not url:
        return None
    url = str(url).strip()
    url = url.rstrip("/")
    url = url.replace("http://", "https://")
    if not url.startswith("https://") and not url.startswith("http://"):
        url = "https://" + url
    return url

def normalize_github(url):
    if not url:
        return None
    url = str(url).strip()
    url = url.rstrip("/")
    url = url.replace("http://", "https://")
    if not url.startswith("https://") and not url.startswith("http://"):
        url = "https://" + url
    return url

def normalize_skill(skill):
    if not skill:
        return ""
    skill = str(skill).strip()
    skill = re.sub(r"^(skills?|experience|email|phone|cgpa|name)\s*[:\-]\s*", "", skill, flags=re.IGNORECASE)
    skill = re.sub(r"^(include|includes|and|or)\s+", "", skill, flags=re.IGNORECASE)
    skill = skill.strip("., ")
    if not skill:
        return ""
    if re.search(r"\b(email|phone|experience|cgpa|candidate|name|project|internship)\b", skill, re.IGNORECASE):
        return ""
    if ":" in skill or "http" in skill or len(skill) > 40:
        return ""
    if re.search(r"\b(has|years|experience|project|internship)\b", skill, re.IGNORECASE):
        return ""
    if re.search(r"\bCAND[-_ ]?\d+\b", skill, re.IGNORECASE):
        return ""
    if re.search(r"\([^)]*CAND[-_ ]?\d+[^)]*\)", skill, re.IGNORECASE):
        return ""
    key = skill.lower().strip()
    if not key:
        return ""
    return SKILL_MAP.get(key, skill.strip())

def normalize_certification(cert):
    if not cert:
        return ""
    cert = str(cert)
    cert = re.sub(
        r"\(.*?\)",
        "",
        cert
    )
    return cert.strip()

def normalize_country(country):
    if not country:
        return None
    key = str(country).lower().strip()
    return COUNTRY_MAP.get(key, key.upper())

def normalize_date(date_str):
    if not date_str:
        return None
    date_str = str(date_str).strip()
    try:
        parsed_date = date_parser.parse(date_str)
        return parsed_date.strftime("%Y-%m")
    except:
        # Fallback to matching YYYY-MM or YYYY patterns
        match = re.search(r"(\d{4})[-/](\d{1,2})", date_str)
        if match:
            year, month = match.group(1), int(match.group(2))
            return f"{year}-{month:02d}"
        match_year = re.search(r"\b(\d{4})\b", date_str)
        if match_year:
            return f"{match_year.group(1)}-01"
        return date_str