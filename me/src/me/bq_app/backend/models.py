from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime

class Recommendation(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    project_id: str
    user_email: str
    job_id: str
    query_hash: str
    query_text: str
    total_billed_gb: float
    estimated_cost_usd: float
    inefficiency_type: str
    recommendation_title: str
    recommendation_details: str
    status: str = "NEW"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda dt: dt.isoformat()
        }
