from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProjectBase(BaseModel):
    model_config = {'protected_namespaces': ()}

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
    model_config = {'protected_namespaces': ()}

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


# API Security Testing Schemas
class ApiSecurityTestCreate(BaseModel):
    project_id: int
    name: str
    target_url: str
    auth_type: Optional[str] = "none"  # none, bearer, api_key, basic, oauth
    auth_credentials: Optional[dict] = {}
    endpoints: List[str] = []
    test_types: List[str] = ["jwt", "bola", "auth", "rate_limit", "mass_assignment"]


class ApiSecurityTestResponse(BaseModel):
    id: int
    project_id: int
    name: str
    target_url: str
    auth_type: Optional[str]
    endpoints: Optional[List[str]]
    test_types: Optional[List[str]]
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_endpoints: int
    vulnerabilities_found: int
    log_file: Optional[str]

    class Config:
        from_attributes = True


class ApiVulnerabilityResponse(BaseModel):
    id: int
    api_test_id: int
    endpoint: str
    method: Optional[str]
    vulnerability_type: str
    severity: str
    title: str
    description: Optional[str]
    proof_of_concept: Optional[str]
    remediation: Optional[str]
    cvss_score: Optional[float]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApiSecurityTestDetail(ApiSecurityTestResponse):
    vulnerabilities: List[ApiVulnerabilityResponse] = []


# Monitoring Schemas
class MonitorCreate(BaseModel):
    project_id: int
    name: str
    monitor_type: str  # api_health, llm_prompt, asset_discovery
    target: str
    configuration: Optional[dict] = {}
    schedule: Optional[str] = "*/5 * * * *"  # cron expression
    alert_threshold: str = "medium"
    notification_channels: List[str] = ["email"]


class MonitorResponse(BaseModel):
    id: int
    project_id: int
    name: str
    monitor_type: str
    target: str
    configuration: Optional[dict]
    schedule: Optional[str]
    is_active: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime
    alert_threshold: str
    notification_channels: Optional[List[str]]

    class Config:
        from_attributes = True


class MonitoringEventResponse(BaseModel):
    id: int
    monitor_id: int
    event_type: str
    severity: str
    title: str
    description: Optional[str]
    event_data: Optional[dict]
    created_at: datetime
    acknowledged: bool

    class Config:
        from_attributes = True


class MonitorDetail(MonitorResponse):
    events: List[MonitoringEventResponse] = []


class AlertResponse(BaseModel):
    id: int
    project_id: int
    alert_type: str
    severity: str
    title: str
    message: Optional[str]
    source_type: Optional[str]
    source_id: Optional[int]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
