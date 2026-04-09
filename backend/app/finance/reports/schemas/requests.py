from datetime import date

from pydantic import BaseModel


class ReportPeriodRequest(BaseModel):
    date_from: date
    date_to: date
