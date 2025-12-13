from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
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
