"""
Database Migration Script
Creates new tables for API Security Testing and Continuous Monitoring features
"""

from database import engine, Base
from models import (
    User, Project, TestRun, Finding,
    ApiSecurityTest, ApiVulnerability,
    Monitor, MonitoringEvent,
    Alert, ScheduledJob
)

def migrate():
    """Create all tables in the database"""
    print("Starting database migration...")

    # This will create all tables defined in models.py that don't exist yet
    Base.metadata.create_all(bind=engine)

    print("✅ Migration completed successfully!")
    print("\nNew tables created:")
    print("  - api_security_tests")
    print("  - api_vulnerabilities")
    print("  - monitors")
    print("  - monitoring_events")
    print("  - alerts")
    print("  - scheduled_jobs")

if __name__ == "__main__":
    migrate()
