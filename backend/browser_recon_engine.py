"""
Browser-Based Reconnaissance Engine (powered by rtrvr.ai)
Uses a real browser agent to crawl target sites and discover forms, inputs, and interactive elements.
"""

import os
import requests
import json
import logging
from typing import Dict, List


RTRVR_API_URL = "https://api.rtrvr.ai/agent"

RECON_SCHEMA = {
    "type": "object",
    "properties": {
        "pages_visited": {
            "type": "array",
            "items": {"type": "string"}
        },
        "forms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_url": {"type": "string"},
                    "form_action": {"type": "string"},
                    "form_method": {"type": "string"},
                    "form_id": {"type": "string"},
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "placeholder": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        "links": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "href": {"type": "string"}
                }
            }
        },
        "search_bars": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_url": {"type": "string"},
                    "input_name": {"type": "string"},
                    "input_id": {"type": "string"},
                    "placeholder": {"type": "string"}
                }
            }
        }
    }
}

RECON_TASK = (
    "Navigate to {url}. Explore the site thoroughly by clicking through the main "
    "navigation menu, links, and any visible buttons. Visit at least 5-10 different pages. "
    "For EVERY page you visit, find ALL forms (login forms, search bars, registration forms, "
    "contact forms, feedback forms, comment forms, file upload forms). For each form, extract "
    "the form action URL, HTTP method, and all input field names and types. Also find any "
    "standalone search bars or input fields not inside a form. Also collect all internal "
    "navigation links you find. Be thorough — check the footer, sidebar, and any dropdown menus."
)


class BrowserReconEngine:
    def __init__(self, target_url: str, logger: logging.Logger = None):
        self.target_url = target_url.rstrip('/')
        self.logger = logger or logging.getLogger(__name__)
        self.api_key = os.environ.get("RTRVR_API_KEY", "")
        self.vulnerabilities = []
        self.discovered_forms: List[Dict] = []

    def run_recon(self) -> Dict:
        """Run browser-based reconnaissance using rtrvr.ai"""
        self.logger.info("=" * 80)
        self.logger.info("Starting Browser-Based Reconnaissance (rtrvr.ai)")
        self.logger.info(f"Target: {self.target_url}")
        self.logger.info("=" * 80)

        if not self.api_key:
            self.logger.warning("RTRVR_API_KEY not set — skipping browser recon")
            return {
                "forms": [],
                "links": [],
                "pages_visited": [],
                "search_bars": [],
                "vulnerabilities": [],
            }

        # Call rtrvr /agent for recon
        task = RECON_TASK.format(url=self.target_url)
        self.logger.info(f"\n[BROWSER RECON] Sending task to rtrvr.ai agent...")
        self.logger.info(f"Task: {task[:200]}...")

        try:
            response = requests.post(
                RTRVR_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "input": task,
                    "urls": [self.target_url],
                    "schema": RECON_SCHEMA,
                    "response": {"verbosity": "final"},
                },
                timeout=120,
            )

            if response.status_code != 200:
                self.logger.error(f"rtrvr API error: {response.status_code} - {response.text[:500]}")
                return self._empty_result()

            data = response.json()
            result = data.get("result", {}).get("json", {})

            # Log usage
            usage = data.get("usage", {})
            if usage:
                self.logger.info(f"rtrvr credits used: {usage.get('creditsUsed', 'N/A')}")

        except requests.exceptions.Timeout:
            self.logger.error("rtrvr API request timed out (120s)")
            return self._empty_result()
        except Exception as e:
            self.logger.error(f"rtrvr API error: {str(e)}")
            return self._empty_result()

        # Parse results
        forms = result.get("forms", [])
        links = result.get("links", [])
        pages_visited = result.get("pages_visited", [])
        search_bars = result.get("search_bars", [])

        self.logger.info(f"\n[BROWSER RECON] Results:")
        self.logger.info(f"  Pages visited: {len(pages_visited)}")
        self.logger.info(f"  Forms discovered: {len(forms)}")
        self.logger.info(f"  Links found: {len(links)}")
        self.logger.info(f"  Search bars found: {len(search_bars)}")

        # Log discovered forms
        for form in forms:
            self.logger.info(f"\n  Form: {form.get('form_action', 'N/A')}")
            self.logger.info(f"    Method: {form.get('form_method', 'N/A')}")
            self.logger.info(f"    Page: {form.get('page_url', 'N/A')}")
            fields = form.get("fields", [])
            for field in fields:
                self.logger.info(f"    Field: {field.get('name', '?')} (type: {field.get('type', '?')})")

        self.discovered_forms = forms

        # Analyze for immediate findings
        self._analyze_findings(forms, search_bars, pages_visited)

        return {
            "forms": forms,
            "links": links,
            "pages_visited": pages_visited,
            "search_bars": search_bars,
            "vulnerabilities": self.vulnerabilities,
        }

    def _analyze_findings(self, forms: List[Dict], search_bars: List[Dict], pages: List[str]) -> None:
        """Analyze discovered elements for security findings"""

        # Check for login forms (potential brute force / injection targets)
        login_forms = [f for f in forms if any(
            kw in json.dumps(f).lower()
            for kw in ["login", "signin", "sign-in", "password", "email"]
        )]

        if login_forms:
            self.logger.info(f"\n  Found {len(login_forms)} login form(s) — potential injection targets")
            for form in login_forms:
                self.add_vulnerability({
                    "endpoint": form.get("form_action", form.get("page_url", "/")),
                    "method": form.get("form_method", "POST").upper(),
                    "vulnerability_type": "exposed_login_form",
                    "severity": "low",
                    "title": f"Login Form Discovered: {form.get('page_url', '/')}",
                    "description": (
                        f"A login form was discovered at {form.get('page_url', '/')} with action "
                        f"'{form.get('form_action', 'N/A')}'. This form accepts user credentials and "
                        f"should be tested for SQL injection, brute force protection, and credential stuffing."
                    ),
                    "proof_of_concept": (
                        f"Form found at: {form.get('page_url', '/')}\n"
                        f"Action: {form.get('form_action', 'N/A')}\n"
                        f"Method: {form.get('form_method', 'N/A')}\n"
                        f"Fields: {json.dumps(form.get('fields', []), indent=2)}"
                    ),
                    "remediation": (
                        "Ensure login forms are protected against brute force attacks (rate limiting, "
                        "account lockout). Use parameterized queries to prevent SQL injection. "
                        "Implement CAPTCHA after failed attempts."
                    ),
                    "cvss_score": 3.0,
                })

        # Check for registration / user creation forms
        reg_forms = [f for f in forms if any(
            kw in json.dumps(f).lower()
            for kw in ["register", "signup", "sign-up", "create account", "new user"]
        )]

        if reg_forms:
            self.logger.info(f"\n  Found {len(reg_forms)} registration form(s)")

        # Check for feedback / comment forms (XSS targets)
        feedback_forms = [f for f in forms if any(
            kw in json.dumps(f).lower()
            for kw in ["feedback", "comment", "review", "message", "contact", "textarea"]
        )]

        if feedback_forms:
            self.logger.info(f"\n  Found {len(feedback_forms)} feedback/comment form(s) — potential stored XSS targets")

        # Check for file upload forms
        upload_forms = [f for f in forms if any(
            field.get("type", "").lower() == "file"
            for field in f.get("fields", [])
        )]

        if upload_forms:
            self.logger.info(f"\n  Found {len(upload_forms)} file upload form(s)")
            for form in upload_forms:
                self.add_vulnerability({
                    "endpoint": form.get("form_action", form.get("page_url", "/")),
                    "method": "POST",
                    "vulnerability_type": "file_upload_form",
                    "severity": "medium",
                    "title": f"File Upload Form Discovered: {form.get('page_url', '/')}",
                    "description": (
                        "A file upload form was discovered. File uploads can be exploited for "
                        "remote code execution, path traversal, or denial of service if not "
                        "properly validated."
                    ),
                    "proof_of_concept": (
                        f"File upload form at: {form.get('page_url', '/')}\n"
                        f"Action: {form.get('form_action', 'N/A')}\n"
                        f"Fields: {json.dumps(form.get('fields', []), indent=2)}"
                    ),
                    "remediation": (
                        "Validate file types, sizes, and content. Store uploads outside web root. "
                        "Use random filenames. Scan for malware."
                    ),
                    "cvss_score": 6.0,
                })

    def _empty_result(self) -> Dict:
        return {
            "forms": [],
            "links": [],
            "pages_visited": [],
            "search_bars": [],
            "vulnerabilities": [],
        }

    def add_vulnerability(self, vuln: Dict) -> None:
        self.vulnerabilities.append(vuln)
        self.logger.warning(f"\n{'*' * 60}")
        self.logger.warning(f"FINDING: {vuln['title']}")
        self.logger.warning(f"Severity: {vuln['severity'].upper()}")
        self.logger.warning(f"{'*' * 60}\n")
