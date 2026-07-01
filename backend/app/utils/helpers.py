from pathlib import Path
from fastapi import UploadFile, HTTPException


# -----------------------------------------
# Allowed file extensions
# -----------------------------------------

ALLOWED_RESUME_EXTENSION = ".pdf"

ALLOWED_ATS_EXTENSION = ".json"


# -----------------------------------------
# Resume Validation
# -----------------------------------------

def validate_resume_file(file: UploadFile):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume file is missing."
        )

    extension = Path(file.filename).suffix.lower()

    if extension != ALLOWED_RESUME_EXTENSION:
        raise HTTPException(
            status_code=400,
            detail="Resume must be a PDF file."
        )


# -----------------------------------------
# ATS Validation
# -----------------------------------------

def validate_ats_file(file: UploadFile):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="ATS file is missing."
        )

    extension = Path(file.filename).suffix.lower()

    if extension != ALLOWED_ATS_EXTENSION:
        raise HTTPException(
            status_code=400,
            detail="ATS must be a JSON file."
        )


# -----------------------------------------
# Save Uploaded File
# -----------------------------------------

async def save_uploaded_file(
    file: UploadFile,
    upload_directory: Path
):

    upload_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = upload_directory / file.filename

    contents = await file.read()

    with open(file_path, "wb") as uploaded_file:
        uploaded_file.write(contents)

    await file.seek(0)

    return file_path