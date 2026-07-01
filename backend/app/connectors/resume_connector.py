from pathlib import Path
import pdfplumber

from app.models.source import CandidateSource
from app.processors.text_processor import TextProcessor
from app.processors.contact_processor import ContactProcessor
from app.processors.profile_processor import ProfileProcessor
from app.processors.experience_processor import ExperienceProcessor
from app.processors.normalization import NormalizationProcessor

from app.utils.logger import logger


class ResumeConnector:
    """
    Resume PDF Connector

    Reads a PDF, extracts the text, processes it,
    and returns a CandidateSource.
    """

    def __init__(self):

        self.text_processor = TextProcessor()
        self.contact_processor = ContactProcessor()
        self.profile_processor = ProfileProcessor()
        self.experience_processor = ExperienceProcessor()

    def extract(self, pdf_path: Path) -> CandidateSource:

        logger.info(f"Reading resume: {pdf_path.name}")

        raw_text = ""

        with pdfplumber.open(pdf_path) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if text:

                    raw_text += text + "\n"

        # -----------------------------
        # Clean text
        # -----------------------------

        cleaned_text = self.text_processor.clean(raw_text)

        # -----------------------------
        # Extract sections
        # -----------------------------

        contact = self.contact_processor.extract(cleaned_text)

        profile = self.profile_processor.extract(cleaned_text)

        experience = self.experience_processor.extract(cleaned_text)

        resume = {

            "contact": contact,

            "profile": profile,

            "experience": experience

        }

        resume = NormalizationProcessor.normalize(resume)

        observations = {

            "full_name": contact.get("name", ""),

            "emails": (
                [contact.get("email")]
                if contact.get("email")
                else []
            ),

            "phones": (
                [contact.get("phone")]
                if contact.get("phone")
                else []
            ),

            "location": contact.get("location") or profile.get("location", ""),

            "headline": profile.get("headline", ""),

            "years_experience": profile.get(
                "years_experience",
                0
            ),

            "skills": profile.get(
                "skills",
                []
            ),

            "experience": experience,

            "education": profile.get(
                "education",
                []
            ),

            "links": {

                "linkedin": contact.get("linkedin"),

                "github": contact.get("github"),

                "portfolio": contact.get("portfolio")

            },

            "projects": profile.get(
                "projects",
                []
            ),

            "certifications": profile.get(
                "certifications",
                []
            ),

            "summary": profile.get(
                "summary",
                ""
            )

        }

        logger.info("Resume processed successfully.")

        return CandidateSource(

            source_id="",

            source_name="Resume PDF",

            source_type="resume",

            filename=pdf_path.name,

            observations=observations,

            parser_confidence=0.97
        )

    def extract_text_source(
        self,
        text: str,
        filename: str,
        source_type: str = "resume_text",
    ) -> CandidateSource:

        logger.info(f"Processing text source: {filename} ({source_type})")

        cleaned_text = self.text_processor.clean(text)

        contact = self.contact_processor.extract(cleaned_text)

        profile = self.profile_processor.extract(cleaned_text)

        experience = self.experience_processor.extract(cleaned_text)

        resume = {
            "contact": contact,
            "profile": profile,
            "experience": experience
        }

        resume = NormalizationProcessor.normalize(resume)

        observations = {
            "full_name": contact.get("name", ""),
            "emails": [contact.get("email")] if contact.get("email") else [],
            "phones": [contact.get("phone")] if contact.get("phone") else [],
            "location": contact.get("location") or profile.get("location", ""),
            "headline": profile.get("headline", ""),
            "years_experience": profile.get("years_experience"),
            "skills": profile.get("skills", []),
            "experience": experience,
            "education": profile.get("education", []),
            "links": {
                "linkedin": contact.get("linkedin"),
                "github": contact.get("github"),
                "portfolio": contact.get("portfolio")
            },
            "projects": profile.get("projects", []),
            "certifications": profile.get("certifications", []),
            "summary": profile.get("summary", "")
        }

        parser_confidence = 0.85 if source_type == "recruiter_notes" else 0.90
        source_name = "Recruiter Notes" if source_type == "recruiter_notes" else "Resume Text"

        return CandidateSource(
            source_id="",
            source_name=source_name,
            source_type=source_type,
            filename=filename,
            observations=observations,
            parser_confidence=parser_confidence
        )