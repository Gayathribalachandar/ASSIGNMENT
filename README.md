# Candidate Intelligence Engine

A Python-based application that combines data from a Resume (PDF) and a Structured Source (CSV or ATS JSON) to generate a single canonical candidate profile. The system compares information from both sources, resolves conflicts, validates the data, and produces a trusted candidate record.

## Features

- Upload one Resume PDF and one CSV or ATS JSON file
- Extract candidate information from multiple sources
- Normalize names, emails, phone numbers, skills, and locations
- Merge data into a single canonical profile
- Resolve conflicting values using rule-based logic
- Calculate field confidence and overall trust score
- Track data provenance
- Validate the final candidate profile
- Generate explainable results with audit information

## Project Structure

```text
Candidate-Intelligence-Engine/
│
├── app/
│   ├── api/
│   ├── connectors/
│   ├── engine/
│   ├── models/
│   ├── services/
│   ├── static/
│   ├── templates/
│   └── main.py
│
├── storage/
├── sample_data/
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+
- FastAPI
- Uvicorn

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Run

Start the application:

```bash
uvicorn app.main:app --reload
```

Open your browser:

```
http://127.0.0.1:8000
```

## Processing Flow

1. Upload one Resume PDF.
2. Upload one CSV or ATS JSON file.
3. Extract candidate information from both sources.
4. Normalize the extracted data.
5. Resolve conflicts between sources.
6. Build a canonical candidate profile.
7. Calculate confidence and trust score.
8. Validate the final profile.
9. Generate the final JSON output.

## Output

The application generates:

- Canonical Candidate Profile
- Trust Score
- Confidence Scores
- Conflict Report
- Provenance Information
- Validation Report
- Audit Information
- Explanation Summary

## Design Decisions

- Modular architecture with separate connectors and processing engines.
- Rule-based conflict resolution for consistent and deterministic results.
- Confidence scoring to measure data reliability.
- Provenance tracking for transparency and explainability.
- Canonical schema to provide a single source of truth.

## Assumptions

- One Resume PDF and one Structured Source are uploaded per request.
- Both files belong to the same candidate.
- Structured files follow the expected format.
- Missing values are handled gracefully without stopping the pipeline.