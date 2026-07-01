import json
from pathlib import Path

from jsonschema import Draft7Validator


class SchemaValidator:
    """
    Validates the canonical candidate and projected output
    against the JSON schemas stored in app/contracts.
    """

    def __init__(self):

        contracts = Path(__file__).resolve().parents[1] / "contracts"

        canonical_path = contracts / "canonical_schema.json"
        projection_path = contracts / "projection_schema.json"

        self.canonical_schema = self._load_schema(canonical_path)
        self.projection_schema = self._load_schema(projection_path)

        self.canonical_validator = (
            Draft7Validator(self.canonical_schema)
            if self.canonical_schema
            else None
        )

        self.projection_validator = (
            Draft7Validator(self.projection_schema)
            if self.projection_schema
            else None
        )

    def _load_schema(self, path: Path):

        if not path.exists():
            return None

        try:
            text = path.read_text(encoding="utf-8").strip()
            if not text:
                return None
            return json.loads(text)
        except Exception:
            return None

    # ----------------------------------------------------

    def validate_canonical(self, candidate: dict):

        if not self.canonical_validator:
            return

        errors = sorted(
            self.canonical_validator.iter_errors(candidate),
            key=lambda e: e.path
        )

        if not errors:
            return

        raise ValueError(
            self._format_errors(errors)
        )

    # ----------------------------------------------------

    def validate_projection(self, projection: dict):

        if not self.projection_validator:
            return

        errors = sorted(
            self.projection_validator.iter_errors(projection),
            key=lambda e: e.path
        )

        if not errors:
            return

        raise ValueError(
            self._format_errors(errors)
        )

    # ----------------------------------------------------

    def _format_errors(self, errors):

        formatted = []

        for error in errors:

            location = ".".join(
                str(x)
                for x in error.path
            )

            if location:

                formatted.append(
                    f"{location}: {error.message}"
                )

            else:

                formatted.append(error.message)

        return "\n".join(formatted)