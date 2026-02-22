# Valkyrie - AI-Powered Security Testing Platform

Valkyrie is an automated security testing platform that discovers vulnerabilities in web applications using AI-driven attack simulation. It combines traditional security testing techniques with browser-based AI agents to detect SQL injection, cross-site scripting (XSS), authentication flaws, and rate limiting issues.

## Features

- **SQL Injection Testing** - Automated detection of SQL injection vulnerabilities across login forms, search endpoints, URL parameters, and API routes. Uses a library of injection payloads with intelligent error pattern matching to identify exploitable entry points.

- **XSS Testing (Browser-Based)** - Client-side cross-site scripting detection powered by [rtrvr.ai](https://rtrvr.ai). Unlike traditional HTTP-based scanners, Valkyrie uses a real browser agent to inject payloads into forms and detect reflected/DOM-based XSS in rendered pages.

- **Authentication Testing** - Tests for common authentication weaknesses including default credentials, brute-force susceptibility, and session management flaws.

- **Rate Limiting Analysis** - Checks whether API endpoints enforce proper rate limits to prevent abuse and denial-of-service attacks.

- **AI-Powered Endpoint Discovery** - Automatically crawls target applications to discover testable endpoints, forms, and API routes before running security tests.

- **PDF Report Generation** - Export detailed vulnerability reports with severity ratings, proof-of-concept details, and remediation recommendations.

- **Real-Time Dashboard** - Monitor running tests, view vulnerability counts by severity, and track your security testing history.

## Tech Stack

| Layer    | Technology                              |
|----------|-----------------------------------------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| Backend  | Python, FastAPI, SQLAlchemy, SQLite      |
| AI/ML    | OpenAI API, rtrvr.ai Browser Agent       |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### 1. Clone the Repository

```bash
git clone <repo-url>
cd LLM-Canvas
```

### 2. Set Up the Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```bash
# Required: OpenAI API key for AI-powered attack generation
OPENAI_API_KEY=your-openai-api-key

# Required for XSS testing: rtrvr.ai API key
# Get yours at https://rtrvr.ai/cloud -> API Keys
RTRVR_API_KEY=your-rtrvr-api-key
```

### 3. Set Up the Frontend

```bash
cd frontend
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
# Runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5000
```

### 5. Open Valkyrie

Visit **http://localhost:5000** in your browser and sign in.

## Recommended Test Target

We recommend using [OWASP Juice Shop](https://juice-shop.herokuapp.com/) as a safe, intentionally vulnerable target for testing:

```
Target URL: https://juice-shop.herokuapp.com/
```

Juice Shop is a modern web application riddled with security flaws, purpose-built for security training and testing. It contains real SQL injection, XSS, and authentication vulnerabilities that Valkyrie can detect.

> **WARNING:** Only use Valkyrie against applications you own or have explicit permission to test. Running security tests against unauthorized targets is illegal and unethical. Juice Shop is a safe, legal target designed for this purpose.

## Usage

1. **Sign in** to the Valkyrie dashboard
2. **Create a new test** - Click "New Test", enter a name and the target URL (e.g., `https://juice-shop.herokuapp.com/`)
3. **Select test types** - Choose from SQL Injection, XSS Testing, Authentication, and Rate Limiting
4. **Run the test** - Valkyrie will automatically discover endpoints and run the selected attacks
5. **Review results** - View discovered vulnerabilities with severity ratings (Critical, High, Medium, Low)
6. **Export report** - Download a PDF report with full findings and remediation steps

## Project Structure

```
LLM-Canvas/
  backend/
    main.py                  # FastAPI server & API routes
    api_security_engine.py   # Test orchestrator - coordinates all engines
    sqli_engine.py           # SQL injection testing engine
    xss_engine.py            # XSS testing via rtrvr.ai browser agent
    database.py              # SQLAlchemy + SQLite configuration
    models.py                # Database models
    .env                     # API keys (not committed)
  frontend/
    src/
      pages/
        Dashboard.tsx        # Security overview & metrics
        APITesting.tsx       # Test management & execution
        APITestDetail.tsx    # Individual test results & vulnerabilities
        Reports.tsx          # PDF report generation
        Settings.tsx         # Platform configuration
      components/
        APITestForm.tsx      # Test creation form
      layouts/
        AppLayout.tsx        # Main app shell with sidebar navigation
```

## Troubleshooting

### Backend won't start
```bash
cd backend
pip install --upgrade -r requirements.txt
python main.py
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Port already in use
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:5000 | xargs kill -9
```

### Database reset
```bash
cd backend
rm llm_auditor.db
python main.py  # Recreates with seed data
```

## License

This project was built for the hackathon. Use responsibly.
