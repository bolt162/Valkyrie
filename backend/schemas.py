from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    model_provider: str
    connection_type: str
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    risk_level: str = "Medium"

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    test_run_count: int = 0
    last_test_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FindingBase(BaseModel):
    title: str
    category: str
    severity: str
    description: Optional[str] = None
    attack_prompt: str
    model_response: Optional[str] = None
    recommendation: Optional[str] = None

class FindingResponse(FindingBase):
    id: int
    test_run_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TestRunBase(BaseModel):
    status: str = "running"

class TestRunResponse(BaseModel):
    id: int
    project_id: int
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    overall_risk_score: Optional[str] = None
    attack_count: int = 0
    project_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class TestRunDetail(TestRunResponse):
    findings: List[FindingResponse] = []

class DashboardStats(BaseModel):
    total_projects: int
    total_test_runs: int
    open_critical_issues: int
    average_risk_score: str

class VulnerabilitySummary(BaseModel):
    critical: int
    high: int
    medium: int
    low: int

class ReportSummary(BaseModel):
    project_name: str
    test_run_date: Optional[datetime]
    overall_risk: Optional[str]
    executive_summary: str
    recommendations: List[str]
    vulnerability_summary: VulnerabilitySummary
    findings: List[FindingResponse]

class SettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    timezone: Optional[str] = None
