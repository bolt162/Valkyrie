# LLM Red Team Auditor

A full-stack SaaS application for automated AI security testing of language models. This tool helps discover vulnerabilities in LLMs before attackers do.

## Overview

The LLM Red Team Auditor provides:
- Automated security testing against LLM models
- Vulnerability detection across multiple attack categories (Jailbreak, Prompt Injection, Data Leakage, Toxic Output, Role Manipulation)
- Dashboard with real-time stats and vulnerability summaries
- Project management for organizing different LLM endpoints
- Detailed test run reports with findings and recommendations
- Executive summaries with actionable security recommendations

## Project Architecture

### Backend (Python/FastAPI)
Located in `/backend/`:
- `main.py` - FastAPI application with all API endpoints
- `models.py` - SQLAlchemy ORM models (User, Project, TestRun, Finding)
- `schemas.py` - Pydantic request/response schemas
- `database.py` - SQLite database connection and session management
- `attack_engine.py` - Red team attack generation and evaluation logic

### Frontend (React/TypeScript/Vite)
Located in `/frontend/`:
- `src/App.tsx` - Main router with all page routes
- `src/lib/api.ts` - Axios API client with TypeScript interfaces
- `src/layouts/AppLayout.tsx` - Sidebar navigation layout
- `src/pages/` - All application pages:
  - Landing.tsx - Public homepage
  - Login.tsx - Authentication page
  - Dashboard.tsx - Overview with stats and recent activity
  - Projects.tsx - Project listing and creation
  - ProjectDetail.tsx - Individual project with test runs
  - TestRunDetail.tsx - Test run findings
  - Reports.tsx - Report listing
  - ReportDetail.tsx - Detailed security report
  - Settings.tsx - User settings
- `src/components/` - Reusable UI components (Badge, Button, Card, Input, Modal, Table)

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite, OpenAI API
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS v4
- **Styling**: Cyberpunk theme with dark background and neon green accents

## Running the Application

Two workflows are configured:
1. **Backend API**: Runs on port 8000 (`cd backend && python main.py`)
2. **Frontend**: Runs on port 5000 (`cd frontend && npm run dev`)

The frontend proxies API requests to `/api/*` which are forwarded to the backend.

## Environment Variables

- `OPENAI_API_KEY` (optional): When set, enables real attack generation and evaluation using OpenAI. When not set, uses mock attack data for demonstration.

## Key Features

1. **Project Management**: Create and manage LLM projects with different connection types (OpenAI-compatible, custom HTTP)
2. **Automated Testing**: Run security test suites against configured models
3. **Vulnerability Detection**: Identify security issues across 5 attack categories
4. **Risk Scoring**: Automatic risk level calculation based on findings
5. **Reports**: Executive summaries with recommendations

## Recent Changes

- Created full-stack application with FastAPI backend and React frontend
- Implemented cyberpunk-themed UI with Tailwind CSS v4
- Added attack engine with OpenAI integration (falls back to mock data)
- Configured Vite proxy for backend API calls
- Added proper TypeScript interfaces for all API responses
- Implemented timeout handling for OpenAI API calls
- Added .gitignore for database files and other artifacts
