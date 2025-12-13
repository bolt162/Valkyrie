import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from openai import OpenAI

from database import engine, get_db, Base
from models import User, Project, TestRun, Finding
from schemas import (
    ProjectCreate, ProjectResponse, TestRunResponse, TestRunDetail,
    FindingResponse, DashboardStats, VulnerabilitySummary, ReportSummary,
    SettingsUpdate
)
from attack_engine import run_attack_engine, generate_executive_summary

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LLM Red Team Auditor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def seed_data(db: Session):
    existing_user = db.query(User).first()
    if existing_user:
        return
    
    user = User(email="security@company.com", company_name="Acme Corp", timezone="UTC")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    demo_project = Project(
        name="GPT-4 Production",
        description="Main production language model for customer support",
        model_provider="OpenAI",
        connection_type="openai-compatible",
        base_url="https://api.openai.com/v1",
        model_name="gpt-4",
        risk_level="Medium",
        user_id=user.id
    )
    db.add(demo_project)
    db.commit()

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    seed_data(db)

@app.get("/health")
def health_check():
    return {"status": "healthy", "openai_configured": bool(os.environ.get("OPENAI_API_KEY"))}

@app.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_projects = db.query(func.count(Project.id)).scalar() or 0
    total_test_runs = db.query(func.count(TestRun.id)).scalar() or 0
    
    critical_count = db.query(func.count(Finding.id)).filter(
        Finding.severity == "Critical"
    ).join(TestRun).filter(TestRun.status == "completed").scalar() or 0
    
    completed_runs = db.query(TestRun).filter(TestRun.status == "completed").all()
    risk_mapping = {"Low": 1, "Medium": 2, "High": 3}
    if completed_runs:
        avg = sum(risk_mapping.get(r.overall_risk_score, 2) for r in completed_runs) / len(completed_runs)
        if avg >= 2.5:
            avg_risk = "High"
        elif avg >= 1.5:
            avg_risk = "Medium"
        else:
            avg_risk = "Low"
    else:
        avg_risk = "N/A"
    
    return DashboardStats(
        total_projects=total_projects,
        total_test_runs=total_test_runs,
        open_critical_issues=critical_count,
        average_risk_score=avg_risk
    )

@app.get("/dashboard/vulnerability-summary", response_model=VulnerabilitySummary)
def get_vulnerability_summary(db: Session = Depends(get_db)):
    def count_severity(sev: str) -> int:
        return db.query(func.count(Finding.id)).filter(Finding.severity == sev).scalar() or 0
    
    return VulnerabilitySummary(
        critical=count_severity("Critical"),
        high=count_severity("High"),
        medium=count_severity("Medium"),
        low=count_severity("Low")
    )

@app.get("/dashboard/recent-testruns", response_model=List[TestRunResponse])
def get_recent_testruns(limit: int = 10, db: Session = Depends(get_db)):
    runs = db.query(TestRun).order_by(TestRun.started_at.desc()).limit(limit).all()
    result = []
    for run in runs:
        result.append(TestRunResponse(
            id=run.id,
            project_id=run.project_id,
            status=run.status,
            started_at=run.started_at,
            finished_at=run.finished_at,
            overall_risk_score=run.overall_risk_score,
            attack_count=run.attack_count,
            project_name=run.project.name if run.project else None
        ))
    return result

@app.get("/projects", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    result = []
    for p in projects:
        test_runs = db.query(TestRun).filter(TestRun.project_id == p.id).all()
        last_run = db.query(TestRun).filter(TestRun.project_id == p.id).order_by(TestRun.started_at.desc()).first()
        
        result.append(ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            model_provider=p.model_provider,
            connection_type=p.connection_type,
            base_url=p.base_url,
            model_name=p.model_name,
            risk_level=p.risk_level,
            created_at=p.created_at,
            test_run_count=len(test_runs),
            last_test_date=last_run.started_at if last_run else None
        ))
    return result

@app.post("/projects", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return ProjectResponse(
        id=db_project.id,
        name=db_project.name,
        description=db_project.description,
        model_provider=db_project.model_provider,
        connection_type=db_project.connection_type,
        base_url=db_project.base_url,
        model_name=db_project.model_name,
        risk_level=db_project.risk_level,
        created_at=db_project.created_at,
        test_run_count=0,
        last_test_date=None
    )

@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    test_runs = db.query(TestRun).filter(TestRun.project_id == project_id).all()
    last_run = db.query(TestRun).filter(TestRun.project_id == project_id).order_by(TestRun.started_at.desc()).first()
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        model_provider=project.model_provider,
        connection_type=project.connection_type,
        base_url=project.base_url,
        model_name=project.model_name,
        risk_level=project.risk_level,
        created_at=project.created_at,
        test_run_count=len(test_runs),
        last_test_date=last_run.started_at if last_run else None
    )

@app.get("/projects/{project_id}/testruns", response_model=List[TestRunResponse])
def get_project_testruns(project_id: int, db: Session = Depends(get_db)):
    runs = db.query(TestRun).filter(TestRun.project_id == project_id).order_by(TestRun.started_at.desc()).all()
    project = db.query(Project).filter(Project.id == project_id).first()
    
    return [TestRunResponse(
        id=r.id,
        project_id=r.project_id,
        status=r.status,
        started_at=r.started_at,
        finished_at=r.finished_at,
        overall_risk_score=r.overall_risk_score,
        attack_count=r.attack_count,
        project_name=project.name if project else None
    ) for r in runs]

@app.post("/projects/{project_id}/testruns", response_model=TestRunResponse)
def create_testrun(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = run_attack_engine(
        project_id=project_id,
        connection_type=project.connection_type,
        base_url=project.base_url,
        model_name=project.model_name,
        api_key=project.api_key,
        db_session=db
    )
    
    test_run = db.query(TestRun).filter(TestRun.id == result["test_run_id"]).first()
    
    return TestRunResponse(
        id=test_run.id,
        project_id=test_run.project_id,
        status=test_run.status,
        started_at=test_run.started_at,
        finished_at=test_run.finished_at,
        overall_risk_score=test_run.overall_risk_score,
        attack_count=test_run.attack_count,
        project_name=project.name
    )

@app.get("/testruns/{test_run_id}", response_model=TestRunDetail)
def get_testrun(test_run_id: int, db: Session = Depends(get_db)):
    test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    
    findings = db.query(Finding).filter(Finding.test_run_id == test_run_id).all()
    
    return TestRunDetail(
        id=test_run.id,
        project_id=test_run.project_id,
        status=test_run.status,
        started_at=test_run.started_at,
        finished_at=test_run.finished_at,
        overall_risk_score=test_run.overall_risk_score,
        attack_count=test_run.attack_count,
        project_name=test_run.project.name if test_run.project else None,
        findings=[FindingResponse(
            id=f.id,
            test_run_id=f.test_run_id,
            title=f.title,
            category=f.category,
            severity=f.severity,
            description=f.description,
            attack_prompt=f.attack_prompt,
            model_response=f.model_response,
            recommendation=f.recommendation,
            created_at=f.created_at
        ) for f in findings]
    )

@app.get("/testruns/{test_run_id}/findings", response_model=List[FindingResponse])
def get_testrun_findings(test_run_id: int, db: Session = Depends(get_db)):
    findings = db.query(Finding).filter(Finding.test_run_id == test_run_id).all()
    return [FindingResponse(
        id=f.id,
        test_run_id=f.test_run_id,
        title=f.title,
        category=f.category,
        severity=f.severity,
        description=f.description,
        attack_prompt=f.attack_prompt,
        model_response=f.model_response,
        recommendation=f.recommendation,
        created_at=f.created_at
    ) for f in findings]

@app.get("/reports", response_model=List[dict])
def get_reports(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    reports = []
    
    for p in projects:
        last_run = db.query(TestRun).filter(
            TestRun.project_id == p.id,
            TestRun.status == "completed"
        ).order_by(TestRun.started_at.desc()).first()
        
        reports.append({
            "project_id": p.id,
            "project_name": p.name,
            "last_test_date": last_run.started_at.isoformat() if last_run else None,
            "overall_risk": last_run.overall_risk_score if last_run else "N/A"
        })
    
    return reports

@app.get("/reports/{project_id}", response_model=ReportSummary)
def get_project_report(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    last_run = db.query(TestRun).filter(
        TestRun.project_id == project_id,
        TestRun.status == "completed"
    ).order_by(TestRun.started_at.desc()).first()
    
    findings = []
    vuln_summary = VulnerabilitySummary(critical=0, high=0, medium=0, low=0)
    
    if last_run:
        db_findings = db.query(Finding).filter(Finding.test_run_id == last_run.id).all()
        findings = [FindingResponse(
            id=f.id,
            test_run_id=f.test_run_id,
            title=f.title,
            category=f.category,
            severity=f.severity,
            description=f.description,
            attack_prompt=f.attack_prompt,
            model_response=f.model_response,
            recommendation=f.recommendation,
            created_at=f.created_at
        ) for f in db_findings]
        
        for f in findings:
            if f.severity == "Critical":
                vuln_summary.critical += 1
            elif f.severity == "High":
                vuln_summary.high += 1
            elif f.severity == "Medium":
                vuln_summary.medium += 1
            else:
                vuln_summary.low += 1
    
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key and findings:
        client = OpenAI(api_key=openai_key)
        summary_data = generate_executive_summary(
            client,
            [{"title": f.title, "category": f.category, "severity": f.severity, "description": f.description} for f in findings],
            project.name
        )
    else:
        summary_data = {
            "summary": f"Security assessment for {project.name}. " + (
                f"Found {len(findings)} vulnerabilities across various categories."
                if findings else "No test runs completed yet."
            ),
            "recommendations": [
                "Review and address all critical findings",
                "Implement input validation",
                "Strengthen system prompts"
            ] if findings else ["Run an initial security assessment"]
        }
    
    return ReportSummary(
        project_name=project.name,
        test_run_date=last_run.started_at if last_run else None,
        overall_risk=last_run.overall_risk_score if last_run else None,
        executive_summary=summary_data["summary"],
        recommendations=summary_data["recommendations"],
        vulnerability_summary=vuln_summary,
        findings=findings
    )

@app.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        return {"email": "security@company.com", "company_name": "", "timezone": "UTC"}
    return {"email": user.email, "company_name": user.company_name or "", "timezone": user.timezone}

@app.put("/settings")
def update_settings(settings: SettingsUpdate, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        user = User(email="security@company.com")
        db.add(user)
    
    if settings.company_name is not None:
        user.company_name = settings.company_name
    if settings.timezone is not None:
        user.timezone = settings.timezone
    
    db.commit()
    return {"message": "Settings updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
