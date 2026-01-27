# How to Run the LLM Security MVP

## Quick Start (Recommended)

### Option 1: Auto Setup & Run
```bash
chmod +x setup-and-run.sh
./setup-and-run.sh
```

### Option 2: Manual Setup

#### Step 1: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

#### Step 2: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

#### Step 3: (Optional) Set OpenAI API Key
```bash
# For real attack generation and evaluation
export OPENAI_API_KEY="sk-your-key-here"

# Skip this if you want to run in demo mode with mock data
```

#### Step 4: Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
# Backend runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5000
```

#### Step 5: Open the App
Visit: **http://localhost:5000**

---

## Demo Mode (No OpenAI API Key)

If you DON'T set `OPENAI_API_KEY`, the app will:
- Use 5 pre-defined mock attack scenarios
- Generate simulated findings
- Work perfectly for client demos
- Show the full UI and workflow

## Full Mode (With OpenAI API Key)

If you DO set `OPENAI_API_KEY`, the app will:
- Generate real attack prompts using GPT-4o-mini
- Test your actual target LLM
- Evaluate responses for real vulnerabilities
- Generate AI-powered executive summaries

---

## Testing the App

1. **Login**: Click "Get Started" or "Login" (no password needed)
2. **Dashboard**: See your stats and recent activity
3. **Projects**: View the demo project "GPT-4 Production"
4. **Run Test**: Click on a project → Click "Run Security Test"
5. **View Results**: See findings, severity levels, attack prompts
6. **Reports**: Check the security report with recommendations

---

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
# Kill processes on ports 8000 and 5000
lsof -ti:8000 | xargs kill -9
lsof -ti:5000 | xargs kill -9
```

### Database issues
```bash
# Reset database
cd backend
rm llm_auditor.db
python main.py  # Will recreate with seed data
```

---

## Environment Variables

Create a `.env` file in the `backend/` directory (optional):
```bash
OPENAI_API_KEY=sk-your-key-here
```

---

## What to Demo to Clients

1. **Dashboard** - Real-time security metrics
2. **Create Project** - Add a new LLM to test
3. **Run Test** - Live security testing
4. **Findings** - Detailed vulnerability breakdown
5. **Reports** - Executive summary with recommendations

---

## Next Steps

- Set up your own OpenAI API key for real testing
- Create projects for your actual LLMs
- Configure target model connections (OpenAI-compatible or custom HTTP)
- Run security tests against production models
- Review and share security reports
