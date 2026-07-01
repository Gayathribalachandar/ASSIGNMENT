from pathlib import Path

from app.connectors.resume_connector import ResumeConnector
from app.connectors.ats_connector import ATSConnector
from app.connectors.recruiter_csv_connector import RecruiterCSVConnector


class ConnectorRegistry:

    def __init__(self):

        self.resume = ResumeConnector()
        self.ats = ATSConnector()
        self.csv = RecruiterCSVConnector()

    def get_connector(self, filename: str):

        extension = Path(filename).suffix.lower()

        if extension == ".pdf":
            return self.resume

        if extension == ".json":
            return self.ats

        if extension == ".csv":
            return self.csv

        raise Exception(
            f"Unsupported file type: {extension}"
        )