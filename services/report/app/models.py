from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ExportFormat(str, Enum):
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"


class ReportOptions(BaseModel):
    include_timeline: bool = True
    include_evidence: bool = True
    include_graph_snapshot: bool = True
    include_executive_summary: bool = True
    format: ExportFormat = ExportFormat.PDF


class ReportGenerateRequest(BaseModel):
    investigation_id: str
    template: str = "default"
    options: ReportOptions = Field(default_factory=ReportOptions)


class ReportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportResponse(BaseModel):
    task_id: str
    status: ReportStatus = ReportStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    investigation_id: str
    format: ExportFormat

    class Config:
        from_attributes = True


class ReportStatusResponse(BaseModel):
    task_id: str
    status: ReportStatus
    progress: Optional[int] = None
    result_url: Optional[str] = None
    error: Optional[str] = None


class EvidenceItem(BaseModel):
    id: str
    type: str
    url: Optional[str] = None
    data: Optional[str] = None
    caption: Optional[str] = None


class TimelineEvent(BaseModel):
    id: str
    timestamp: datetime
    event_type: str
    description: str
    source: Optional[str] = None


class ReportData(BaseModel):
    investigation_id: str
    title: str
    executive_summary: str
    timeline: List[TimelineEvent] = []
    evidence: List[EvidenceItem] = []
    graph_snapshot_url: Optional[str] = None
    metadata: Dict[str, Any] = {}