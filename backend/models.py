from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    company_name = Column(String(255), nullable=True)
    timezone = Column(String(100), default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    model_provider = Column(String(100), nullable=False)
    connection_type = Column(String(50), nullable=False)
    base_url = Column(String(500), nullable=True)
    model_name = Column(String(255), nullable=True)
    api_key = Column(String(500), nullable=True)
    risk_level = Column(String(20), default="Medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    owner = relationship("User", back_populates="projects")
    test_runs = relationship("TestRun", back_populates="project", cascade="all, delete-orphan")

class TestRun(Base):
    __tablename__ = "test_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status = Column(String(50), default="running")
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    overall_risk_score = Column(String(20), nullable=True)
    attack_count = Column(Integer, default=0)
    
    project = relationship("Project", back_populates="test_runs")
    findings = relationship("Finding", back_populates="test_run", cascade="all, delete-orphan")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    attack_prompt = Column(Text, nullable=False)
    model_response = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_run = relationship("TestRun", back_populates="findings")


# API Security Testing Models
class ApiSecurityTest(Base):
    __tablename__ = "api_security_tests"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    target_url = Column(String(500), nullable=False)
    auth_type = Column(String(50), nullable=True)  # none, bearer, api_key, basic, oauth
    auth_credentials = Column(Text, nullable=True)  # JSON: {token, key, username, password}
    endpoints = Column(Text, nullable=True)  # JSON array of endpoints to test
    test_types = Column(Text, nullable=True)  # JSON array: ["jwt", "bola", "rate_limit", "mass_assignment"]
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    total_endpoints = Column(Integer, default=0)
    vulnerabilities_found = Column(Integer, default=0)
    log_file = Column(String(500), nullable=True)

    project = relationship("Project")
    vulnerabilities = relationship("ApiVulnerability", back_populates="api_test", cascade="all, delete-orphan")


class ApiVulnerability(Base):
    __tablename__ = "api_vulnerabilities"

    id = Column(Integer, primary_key=True, index=True)
    api_test_id = Column(Integer, ForeignKey("api_security_tests.id"), nullable=False)
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    vulnerability_type = Column(String(100), nullable=False)  # jwt_weak, bola, broken_auth, rate_limit_missing
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    proof_of_concept = Column(Text, nullable=True)  # The actual exploit/request
    remediation = Column(Text, nullable=True)
    cvss_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="open")  # open, fixed, false_positive, accepted_risk

    api_test = relationship("ApiSecurityTest", back_populates="vulnerabilities")


# Continuous Monitoring Models
class Monitor(Base):
    __tablename__ = "monitors"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    monitor_type = Column(String(50), nullable=False)  # api_health, llm_prompt, asset_discovery
    target = Column(String(500), nullable=False)
    configuration = Column(Text, nullable=True)  # JSON: monitoring-specific config
    schedule = Column(String(50), nullable=True)  # cron expression: "*/5 * * * *" (every 5 min)
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    alert_threshold = Column(String(50), default="medium")  # low, medium, high, critical
    notification_channels = Column(Text, nullable=True)  # JSON: ["email", "slack", "webhook"]

    project = relationship("Project")
    events = relationship("MonitoringEvent", back_populates="monitor", cascade="all, delete-orphan")


class MonitoringEvent(Base):
    __tablename__ = "monitoring_events"

    id = Column(Integer, primary_key=True, index=True)
    monitor_id = Column(Integer, ForeignKey("monitors.id"), nullable=False)
    event_type = Column(String(100), nullable=False)  # new_vulnerability, service_down, anomaly_detected
    severity = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_data = Column(Text, nullable=True)  # JSON: event-specific data
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)

    monitor = relationship("Monitor", back_populates="events")


# Alert System Models
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # vulnerability, service_down, anomaly
    severity = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=True)  # api_test, monitor, llm_test
    source_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project")


# Scheduled Jobs Tracking
class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(50), nullable=False)  # api_test, monitor
    target_id = Column(Integer, nullable=True)  # ID of api_test or monitor
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    scheduled_for = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
