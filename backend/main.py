import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

from database import engine, get_db, Base
from models import (
    User, Project, TestRun, Finding,
    ApiSecurityTest, ApiVulnerability,
    Monitor, MonitoringEvent, Alert
)
from schemas import (
    ProjectCreate, ProjectResponse, TestRunResponse, TestRunDetail,
    FindingResponse, DashboardStats, VulnerabilitySummary, ReportSummary,
    SettingsUpdate,
    ApiSecurityTestCreate, ApiSecurityTestResponse, ApiSecurityTestDetail,
    ApiVulnerabilityResponse,
    MonitorCreate, MonitorResponse, MonitorDetail, MonitoringEventResponse,
    AlertResponse
)
from attack_engine import run_attack_engine, generate_executive_summary
from api_security_engine import ApiSecurityEngine, setup_logging as setup_api_logging
from report_generator import generate_security_report
from api_discovery_engine import ApiDiscoveryEngine, setup_discovery_logging
import json
import threading

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


# ============================================================================
# API SECURITY TESTING ENDPOINTS
# ============================================================================

@app.post("/api-tests", response_model=ApiSecurityTestResponse)
def create_api_test(test: ApiSecurityTestCreate, db: Session = Depends(get_db)):
    """Create a new API security test"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == test.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create test record
    api_test = ApiSecurityTest(
        project_id=test.project_id,
        name=test.name,
        target_url=test.target_url,
        auth_type=test.auth_type,
        auth_credentials=json.dumps(test.auth_credentials),
        endpoints=json.dumps(test.endpoints),
        test_types=json.dumps(test.test_types),
        status="pending",
        total_endpoints=len(test.endpoints)
    )

    db.add(api_test)
    db.commit()
    db.refresh(api_test)

    # Parse JSON fields for response
    response = ApiSecurityTestResponse(
        id=api_test.id,
        project_id=api_test.project_id,
        name=api_test.name,
        target_url=api_test.target_url,
        auth_type=api_test.auth_type,
        endpoints=json.loads(api_test.endpoints) if api_test.endpoints else [],
        test_types=json.loads(api_test.test_types) if api_test.test_types else [],
        status=api_test.status,
        created_at=api_test.created_at,
        started_at=api_test.started_at,
        completed_at=api_test.completed_at,
        total_endpoints=api_test.total_endpoints,
        vulnerabilities_found=api_test.vulnerabilities_found,
        log_file=api_test.log_file
    )

    return response


@app.get("/api-tests", response_model=List[ApiSecurityTestResponse])
def list_api_tests(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    """List all API security tests, optionally filtered by project"""
    # Force fresh read from DB — background thread may have updated status
    db.expire_all()
    query = db.query(ApiSecurityTest)

    if project_id:
        query = query.filter(ApiSecurityTest.project_id == project_id)

    tests = query.order_by(ApiSecurityTest.created_at.desc()).all()

    # Parse JSON fields
    results = []
    for test in tests:
        results.append(ApiSecurityTestResponse(
            id=test.id,
            project_id=test.project_id,
            name=test.name,
            target_url=test.target_url,
            auth_type=test.auth_type,
            endpoints=json.loads(test.endpoints) if test.endpoints else [],
            test_types=json.loads(test.test_types) if test.test_types else [],
            status=test.status,
            created_at=test.created_at,
            started_at=test.started_at,
            completed_at=test.completed_at,
            total_endpoints=test.total_endpoints,
            vulnerabilities_found=test.vulnerabilities_found,
            log_file=test.log_file
        ))

    return results


@app.get("/api-tests/{test_id}", response_model=ApiSecurityTestDetail)
def get_api_test(test_id: int, db: Session = Depends(get_db)):
    """Get details of a specific API security test"""
    test = db.query(ApiSecurityTest).filter(ApiSecurityTest.id == test_id).first()

    if not test:
        raise HTTPException(status_code=404, detail="API test not found")

    # Get vulnerabilities
    vulnerabilities = db.query(ApiVulnerability).filter(
        ApiVulnerability.api_test_id == test_id
    ).all()

    return ApiSecurityTestDetail(
        id=test.id,
        project_id=test.project_id,
        name=test.name,
        target_url=test.target_url,
        auth_type=test.auth_type,
        endpoints=json.loads(test.endpoints) if test.endpoints else [],
        test_types=json.loads(test.test_types) if test.test_types else [],
        status=test.status,
        created_at=test.created_at,
        started_at=test.started_at,
        completed_at=test.completed_at,
        total_endpoints=test.total_endpoints,
        vulnerabilities_found=test.vulnerabilities_found,
        log_file=test.log_file,
        vulnerabilities=[ApiVulnerabilityResponse.model_validate(v) for v in vulnerabilities]
    )


def run_api_security_test_background(test_id: int, db_url: str):
    """Background function to run API security test"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Create new DB session for background thread
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Get test record
        test = db.query(ApiSecurityTest).filter(ApiSecurityTest.id == test_id).first()
        if not test:
            return

        # Update status
        test.status = "running"
        test.started_at = datetime.utcnow()
        db.commit()

        # Setup logging
        logger, log_filename = setup_api_logging(test_id)
        test.log_file = log_filename
        db.commit()

        logger.info("="*80)
        logger.info(f"Starting API Security Test: {test.name}")
        logger.info(f"Target: {test.target_url}")
        logger.info("="*80)

        # Parse JSON fields
        auth_config = json.loads(test.auth_credentials) if test.auth_credentials else {}
        auth_config['type'] = test.auth_type
        endpoints = json.loads(test.endpoints) if test.endpoints else []
        test_types = json.loads(test.test_types) if test.test_types else []

        # Run security tests
        sec_engine = ApiSecurityEngine(
            target_url=test.target_url,
            auth_config=auth_config,
            logger=logger
        )

        vulnerabilities = sec_engine.run_all_tests(endpoints, test_types)

        # Save vulnerabilities to database
        for vuln in vulnerabilities:
            api_vuln = ApiVulnerability(
                api_test_id=test_id,
                endpoint=vuln['endpoint'],
                method=vuln.get('method'),
                vulnerability_type=vuln['vulnerability_type'],
                severity=vuln['severity'],
                title=vuln['title'],
                description=vuln.get('description'),
                proof_of_concept=vuln.get('proof_of_concept'),
                remediation=vuln.get('remediation'),
                cvss_score=vuln.get('cvss_score'),
                status='open'
            )
            db.add(api_vuln)

        # Update test status
        test.status = "completed"
        test.completed_at = datetime.utcnow()
        test.vulnerabilities_found = len(vulnerabilities)
        db.commit()

        logger.info("="*80)
        logger.info(f"Test completed. Found {len(vulnerabilities)} vulnerabilities")
        logger.info("="*80)

        # Create alert for critical/high vulnerabilities
        critical_high = [v for v in vulnerabilities if v['severity'] in ['critical', 'high']]
        if critical_high:
            alert = Alert(
                project_id=test.project_id,
                alert_type='vulnerability',
                severity='high' if any(v['severity'] == 'critical' for v in critical_high) else 'medium',
                title=f'API Security Test Found {len(critical_high)} Critical/High Vulnerabilities',
                message=f'Test "{test.name}" discovered {len(critical_high)} critical/high severity vulnerabilities.',
                source_type='api_test',
                source_id=test_id,
                is_read=False
            )
            db.add(alert)
            db.commit()

    except Exception as e:
        test.status = "failed"
        test.completed_at = datetime.utcnow()
        db.commit()
        print(f"Error running API security test: {str(e)}")

    finally:
        db.close()


@app.post("/api-tests/{test_id}/run")
def run_api_test(test_id: int, db: Session = Depends(get_db)):
    """Start an API security test"""
    test = db.query(ApiSecurityTest).filter(ApiSecurityTest.id == test_id).first()

    if not test:
        raise HTTPException(status_code=404, detail="API test not found")

    if test.status == "running":
        raise HTTPException(status_code=400, detail="Test is already running")

    # Get database URL
    from database import SQLALCHEMY_DATABASE_URL

    # Start test in background thread
    thread = threading.Thread(
        target=run_api_security_test_background,
        args=(test_id, SQLALCHEMY_DATABASE_URL)
    )
    thread.daemon = True
    thread.start()

    return {"message": "API security test started", "test_id": test_id}


@app.get("/api-tests/{test_id}/vulnerabilities", response_model=List[ApiVulnerabilityResponse])
def get_api_vulnerabilities(test_id: int, db: Session = Depends(get_db)):
    """Get vulnerabilities found in an API security test"""
    vulnerabilities = db.query(ApiVulnerability).filter(
        ApiVulnerability.api_test_id == test_id
    ).all()

    return [ApiVulnerabilityResponse.model_validate(v) for v in vulnerabilities]


@app.get("/api-tests/{test_id}/report")
def download_api_test_report(test_id: int, db: Session = Depends(get_db)):
    """Generate and download PDF report for an API security test"""

    # Get test data
    test = db.query(ApiSecurityTest).filter(ApiSecurityTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="API test not found")

    # Get vulnerabilities
    vulnerabilities = db.query(ApiVulnerability).filter(
        ApiVulnerability.api_test_id == test_id
    ).all()

    # Prepare test data for report
    test_data = {
        'name': test.name,
        'target_url': test.target_url,
        'auth_type': test.auth_type,
        'status': test.status,
        'created_at': test.created_at.strftime('%Y-%m-%d %H:%M:%S') if test.created_at else 'N/A',
        'completed_at': test.completed_at.strftime('%Y-%m-%d %H:%M:%S') if test.completed_at else 'N/A',
    }

    # Prepare findings data
    findings_data = []
    for vuln in vulnerabilities:
        findings_data.append({
            'title': vuln.title,
            'severity': vuln.severity,
            'vulnerability_type': vuln.vulnerability_type,
            'endpoint': vuln.endpoint,
            'method': vuln.method,
            'description': vuln.description,
            'proof_of_concept': vuln.proof_of_concept,
            'remediation': vuln.remediation,
            'cvss_score': vuln.cvss_score,
        })

    # Generate PDF
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    pdf_filename = f"security_report_{test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(reports_dir, pdf_filename)

    try:
        generate_security_report(test_data, findings_data, pdf_path)

        return FileResponse(
            path=pdf_path,
            filename=f"Valkyrie_Security_Report_{test.name.replace(' ', '_')}.pdf",
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Valkyrie_Security_Report_{test.name.replace(' ', '_')}.pdf"
            }
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generating report:\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


# ============================================================================
# ALERTS ENDPOINTS
# ============================================================================

@app.get("/alerts", response_model=List[AlertResponse])
def list_alerts(
    project_id: Optional[int] = None,
    is_read: Optional[bool] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List alerts, optionally filtered"""
    query = db.query(Alert)

    if project_id:
        query = query.filter(Alert.project_id == project_id)

    if is_read is not None:
        query = query.filter(Alert.is_read == is_read)

    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()

    return [AlertResponse.model_validate(a) for a in alerts]


@app.put("/alerts/{alert_id}/read")
def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as read"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    db.commit()

    return {"message": "Alert marked as read"}


@app.get("/alerts/unread-count")
def get_unread_alert_count(db: Session = Depends(get_db)):
    """Get count of unread alerts"""
    count = db.query(func.count(Alert.id)).filter(Alert.is_read == False).scalar() or 0
    return {"unread_count": count}


# ============================================================================
# API DISCOVERY ENDPOINTS
# ============================================================================

@app.post("/api-discovery/discover")
def discover_apis(request: dict):
    """
    Automatically discover API endpoints from a target URL

    Request body:
    {
        "target_url": "https://example.com"
    }
    """
    target_url = request.get('target_url')

    if not target_url:
        raise HTTPException(status_code=400, detail="target_url is required")

    try:
        # Create discovery engine
        logger, log_filename = setup_discovery_logging(0)  # Use 0 as temp ID
        engine = ApiDiscoveryEngine(target_url, logger)

        # Run discovery
        results = engine.discover_all()

        return {
            "success": True,
            "target_url": target_url,
            "discoveries": results,
            "log_file": log_filename
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "discoveries": {
                "endpoints": [],
                "subdomains": [],
                "technologies": {},
                "api_documentation": []
            }
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
