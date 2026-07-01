import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.candidate_service import CandidateService


def load_source(spec: str) -> Dict[str, Any]:
    source_type, file_path = spec.split(":", 1)
    path = Path(file_path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        data = {"text": text}
    return {"type": source_type, "data": data}


def main() -> None:
    parser = argparse.ArgumentParser(description="Transform candidate sources into one canonical profile.")
    parser.add_argument("--source", action="append", required=True, help="source_type:path, e.g. ats_json:sample_data/ats/candidate.json")
    parser.add_argument("--config", help="Optional projection config JSON path")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    sources: List[Dict[str, Any]] = [load_source(spec) for spec in args.source]
    config = json.loads(Path(args.config).read_text(encoding="utf-8")) if args.config else None
    result = CandidateService.transform(sources, config)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
