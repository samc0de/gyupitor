from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class QueryJobBase(BaseModel):
    job_id: str
    query_hash: str
    project_id: Optional[str] = None
    user_email: Optional[str] = None
    total_bytes_billed: Optional[int] = None
    total_slot_ms: Optional[int] = None
    creation_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timeline_details_file: Optional[str] = None

    class Config:
        from_attributes = True

class QueryJobCreate(QueryJobBase):
    pass

class QueryJob(QueryJobBase):
    pass

class RawQueryBase(BaseModel):
    query_hash: str
    query_text: str

    class Config:
        from_attributes = True

class RawQueryCreate(RawQueryBase):
    pass

class RawQuery(RawQueryBase):
    pass

class ExecutionTimelineBase(BaseModel):
    job_id: str
    timeline_json: str

    class Config:
        from_attributes = True

class ExecutionTimelineCreate(ExecutionTimelineBase):
    pass

class ExecutionTimeline(ExecutionTimelineBase):
    pass

class QueryJobWithDetails(QueryJob):
    raw_query: Optional[RawQuery] = None
    execution_timeline: Optional[ExecutionTimeline] = None

class QueryStats(BaseModel):
    query_hash: str
    total_bytes_billed: int
    total_slot_ms: int
    job_count: int
    avg_bytes_billed: float
    avg_slot_ms: float
    query_text_snippet: str

    class Config:
        from_attributes = True

class DailyCost(BaseModel):
    date: str
    total_bytes_billed: int

    class Config:
        from_attributes = True

class ProjectCost(BaseModel):
    project_id: str
    total_bytes_billed: int

    class Config:
        from_attributes = True

class UserCost(BaseModel):
    user_email: str
    total_bytes_billed: int

    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    total_cost_tb: float
    total_queries_analyzed: int
    top_spender_email: Optional[str] = None
    top_spender_cost_tb: Optional[float] = None
    last_analyzed_date: Optional[datetime] = None

    class Config:
        from_attributes = True