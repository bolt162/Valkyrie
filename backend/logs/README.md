# Attack Engine Logs

This directory contains detailed logs from security test runs.

## Log File Format

Files are named: `test_run_{test_run_id}_{timestamp}.log`

Example: `test_run_7_20251215_093045.log`

## What's Logged

Each log file contains:

### 1. Test Run Metadata
- Test Run ID
- Project ID
- Target model configuration
- Timestamp

### 2. Attack Generation (Step 1)
- OpenAI API request to generate attacks
- Generated attack prompts
- Attack categories and titles

### 3. Target Model Testing (Step 2)
- Each attack prompt sent to target model
- Full target model responses
- Response metadata (length, timing)

### 4. Response Evaluation (Step 3)
- OpenAI evaluation of each response
- Vulnerability determination (yes/no)
- Severity assessment
- Detailed descriptions and recommendations

### 5. Final Summary
- Total attacks executed
- Vulnerabilities found
- Overall risk score
- Test duration

## How to Use

### View Latest Test
```bash
ls -lt backend/logs/ | head -5
cat backend/logs/test_run_7_20251215_093045.log
```

### Search for Vulnerabilities
```bash
grep "VULNERABILITY DETECTED" backend/logs/*.log
```

### Find Specific Attack
```bash
grep -A 20 "Jailbreak" backend/logs/test_run_7_*.log
```

### Export for Analysis
```bash
# Copy to your analysis directory
cp backend/logs/test_run_*.log ~/analysis/
```

## Log Levels

- **INFO**: Normal operation (attack execution, responses)
- **WARNING**: Important notices (demo mode, vulnerabilities detected)
- **ERROR**: Failures (API errors, evaluation failures)
- **DEBUG**: Detailed raw data (full API responses)

## Privacy & Security

⚠️ **Warning**: Log files contain:
- Attack prompts (potentially harmful content)
- Model responses (may include sensitive data if leaked)
- API keys in request metadata (masked in production)

**Do not commit log files to version control!**

They are automatically excluded via `.gitignore`.
