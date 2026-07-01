from pathlib import Path
from time import perf_counter
from typing import List, Dict, Any, Optional

from fastapi import UploadFile

from app.connectors.connector_registry import ConnectorRegistry
from app.engine.identity_resolution_engine import IdentityResolutionEngine
from app.engine.resolution_engine import ResolutionEngine
from app.engine.projection_engine import ProjectionEngine
from app.engine.explanation_engine import ExplanationEngine
from app.engine.validation_engine import ValidationEngine
from app.engine.decision_engine import DecisionEngine
from app.engine.audit_engine import AuditEngine
from app.engine.rule_engine import RuleEngine
from app.engine.schema_validator import SchemaValidator

from app.utils.helpers import save_uploaded_file
from app.utils.logger import logger

from app.models.source import CandidateSource


class CandidateService:

    def __init__(self):

        self.upload_directory = Path("storage/uploads")
        self.upload_directory.mkdir(parents=True, exist_ok=True)

        self.registry = ConnectorRegistry()

        self.identity_engine = IdentityResolutionEngine()
        self.resolution_engine = ResolutionEngine()
        self.projection_engine = ProjectionEngine()

        self.explanation_engine = ExplanationEngine()
        self.validation_engine = ValidationEngine()
        self.decision_engine = DecisionEngine()
        self.audit_engine = AuditEngine()
        self.rule_engine = RuleEngine()

        self.schema_validator = SchemaValidator()

    async def process_uploads(
        self,
        resumes: List[UploadFile],
        structured_files: List[UploadFile]
    ):

        logger.info("Starting Candidate Processing")

        start = perf_counter()

        if len(resumes) != 1:
            raise Exception("Please upload exactly one Resume PDF.")

        if len(structured_files) != 1:
            raise Exception("Please upload exactly one CSV or ATS JSON.")

        sources: List[CandidateSource] = []

        # -------------------------------------------------------
        # Resume
        # -------------------------------------------------------

        resume = resumes[0]

        logger.info(f"Reading resume : {resume.filename}")

        resume_path = await save_uploaded_file(
            resume,
            self.upload_directory
        )

        resume_connector = self.registry.get_connector(
            resume.filename
        )

        resume_source = resume_connector.extract(
            resume_path
        )

        resume_source.filename = resume.filename

        sources.append(resume_source)

        # -------------------------------------------------------
        # Structured File
        # -------------------------------------------------------

        structured = structured_files[0]

        logger.info(
            f"Reading structured file : {structured.filename}"
        )

        structured_path = await save_uploaded_file(
            structured,
            self.upload_directory
        )

        structured_connector = self.registry.get_connector(
            structured.filename
        )

        structured_source = structured_connector.extract(
            structured_path
        )

        structured_source.filename = structured.filename

        sources.append(structured_source)

        # -------------------------------------------------------
        # Identity Resolution
        # -------------------------------------------------------

        groups = self.identity_engine.group_candidates(
            sources
        )

        if not groups:
            raise Exception("Unable to identify candidate.")

        group = groups[0]

        logger.info("Resolving candidate...")

        candidate = self.resolution_engine.resolve(
            group
        )

        candidate.overall_confidence = candidate.trust_score

        logger.info("Projecting candidate...")

        candidate_dict = self.projection_engine.project(
            candidate,
            {
                "missing_policy": "null",
                "include_confidence": False,
                "include_provenance": False,
                "include_conflicts": True
            }
        )

        processing_time = round(
            perf_counter() - start,
            2
        )

        logger.info("Building response...")

        return self._build_response(
            candidate=candidate,
            candidate_dict=candidate_dict,
            sources=sources,
            processing_time=processing_time
        )
    # ---------------------------------------------------
# BUILD RESPONSE
# ---------------------------------------------------

    def _build_response(
        self,
        candidate,
        candidate_dict,
        sources,
        processing_time
    ):

        score = round(candidate.trust_score, 2)

        if score >= 90:
            trust_level = "High Trust"
        elif score >= 70:
            trust_level = "Medium Trust"
        else:
            trust_level = "Low Trust"

        validation = self.validation_engine.validate(candidate)

        decision = self.decision_engine.decide(candidate)

        audit = self.audit_engine.build(candidate)

        rules = self.rule_engine.evaluate(candidate)

        explanation = self.explanation_engine.build_summary(candidate)

        return {

            "success": True,

            "processing_time": processing_time,

            "trust_score": score,

            "trust_level": trust_level,

            "candidate": candidate_dict,

            "validation": validation,

            "decision": decision,

            "audit": audit,

            "rules": rules,

            "explanation": {

            "summary": explanation,

            "overall_score": score,

            "field_confidence": candidate.confidence,

            "provenance": candidate.provenance,

            "conflicts": candidate.conflicts,

            "sources": [

                {

                    "filename": s.filename,

                    "source_type": s.source_type,

                    "parser_confidence": s.parser_confidence

                }

                for s in sources

            ]

        }

    }
