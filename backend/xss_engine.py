"""
XSS Testing Engine (powered by rtrvr.ai)
Uses a real browser agent to inject XSS payloads into forms and detect
reflected, stored, and DOM-based cross-site scripting vulnerabilities.

Designed for focused, fast rtrvr calls (~30-60s each) — one page, one action.
"""

import os
import requests
import json
import logging
import uuid
from typing import Dict, List
from urllib.parse import urljoin


RTRVR_API_URL = "https://api.rtrvr.ai/agent"

# Single best payload — IMG onerror is fast and reliably detected
def _make_payload(marker: str) -> Dict:
    """One payload per target. IMG onerror is the most effective for detection."""
    return {
        "name": "IMG Onerror",
        "payload": f'<img src=x onerror="document.title=\'VALKYRIE_XSS_{marker}\'">',
        "detect_in_title": True,
    }


XSS_DETECT_SCHEMA = {
    "type": "object",
    "properties": {
        "page_title_after_submit": {"type": "string"},
        "marker_found_in_page": {"type": "boolean"},
        "marker_context": {"type": "string"},
        "form_submitted_successfully": {"type": "boolean"},
        "error_message": {"type": "string"},
        "page_content_snippet": {"type": "string"},
    }
}

# Known pages/endpoints that typically have injectable forms
SEARCH_INDICATORS = ["search", "q=", "query", "find"]
FORM_PAGES = [
    # Home page search is already covered by _test_search_xss — skip it
    {"path": "/#/contact", "description": "Contact/Feedback form", "field_hint": "comment"},
]

# Max rtrvr calls to keep total XSS time reasonable (~6 min max)
MAX_RTRVR_CALLS = 3


class XSSEngine:
    def __init__(self, target_url: str, logger: logging.Logger = None):
        self.target_url = target_url.rstrip('/')
        self.logger = logger or logging.getLogger(__name__)
        self.api_key = os.environ.get("RTRVR_API_KEY", "")
        self.vulnerabilities: List[Dict] = []
        self._rtrvr_calls = 0  # Track calls to enforce MAX_RTRVR_CALLS

    def _budget_exhausted(self) -> bool:
        """Check if we've hit the max rtrvr call budget."""
        if self._rtrvr_calls >= MAX_RTRVR_CALLS:
            self.logger.info(f"  [Budget] Hit max rtrvr calls ({MAX_RTRVR_CALLS}), skipping remaining tests")
            return True
        return False

    def run_all_tests(self, endpoints: List[str] = None) -> List[Dict]:
        """
        Run XSS tests using rtrvr browser agent.

        Strategy: 1 payload per target, max 3 rtrvr calls total (~6 min).
        Tests 3 distinct attack surfaces:
          1. Search bar (DOM interaction)
          2. URL parameter injection (direct URL)
          3. Contact/feedback form (form submission)

        Each rtrvr call is a focused, single-action task for speed.
        """
        self.logger.info("=" * 80)
        self.logger.info("Starting XSS Testing (rtrvr.ai Browser Agent)")
        self.logger.info(f"Budget: max {MAX_RTRVR_CALLS} rtrvr calls (~{MAX_RTRVR_CALLS * 2} min)")
        self.logger.info("=" * 80)

        if not self.api_key:
            self.logger.warning("RTRVR_API_KEY not set - skipping XSS testing")
            return []

        endpoints = endpoints or []
        self._rtrvr_calls = 0

        # 1. Test search bar on the main page (most common XSS vector)
        self._test_search_xss()

        # 2. Test first URL-based search endpoint (e.g., /rest/products/search?q=)
        if not self._budget_exhausted():
            search_endpoints = [
                ep for ep in endpoints
                if any(indicator in ep.lower() for indicator in SEARCH_INDICATORS)
            ]
            if search_endpoints:
                self._test_url_param_xss(search_endpoints[0])

        # 3. Test contact/feedback form (different attack surface than search)
        if not self._budget_exhausted():
            for form_page in FORM_PAGES:
                if self._budget_exhausted():
                    break
                page_url = self.target_url + form_page["path"]
                self._test_page_form_xss(
                    page_url,
                    form_page["description"],
                    form_page["field_hint"],
                )

        self.logger.info("=" * 80)
        self.logger.info(f"XSS testing complete. {self._rtrvr_calls} rtrvr calls used, {len(self.vulnerabilities)} vulnerabilities found")
        self.logger.info("=" * 80)

        return self.vulnerabilities

    def _call_rtrvr(self, task: str, page_url: str) -> Dict:
        """Make a single rtrvr API call. Returns parsed result or empty dict."""
        try:
            response = requests.post(
                RTRVR_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "input": task,
                    "urls": [page_url],
                    "schema": XSS_DETECT_SCHEMA,
                    "response": {"verbosity": "final"},
                },
                timeout=120,
            )

            if response.status_code != 200:
                self.logger.error(f"  rtrvr API error: {response.status_code}")
                return {}

            data = response.json()

            # Handle rtrvr error responses
            if data.get("error"):
                self.logger.error(f"  rtrvr error: {data['error']}")
                return {}

            return data.get("result", {}).get("json", {})

        except requests.exceptions.Timeout:
            self.logger.error("  rtrvr API timeout (120s)")
            return {}
        except Exception as e:
            self.logger.error(f"  rtrvr API exception: {str(e)}")
            return {}

    def _check_xss_result(self, result: Dict, marker: str, payload_info: Dict,
                           page_url: str, field_name: str, method: str = "GET") -> bool:
        """Check rtrvr result for XSS indicators. Returns True if vulnerability found."""
        if not result:
            return False

        marker_found = result.get("marker_found_in_page", False)
        page_title = result.get("page_title_after_submit", "")
        marker_context = result.get("marker_context", "")
        content_snippet = result.get("page_content_snippet", "")

        title_changed = f"VALKYRIE_XSS_{marker}" in str(page_title)
        reflected = marker_found or f"VALKYRIE_XSS_{marker}" in str(content_snippet)

        if title_changed:
            self.logger.warning(f"  CRITICAL: XSS payload executed! Title changed to marker.")
            self.add_vulnerability({
                "endpoint": page_url,
                "method": method,
                "vulnerability_type": "xss_reflected",
                "severity": "critical",
                "title": f"Reflected XSS (JS Execution) via '{field_name}'",
                "description": (
                    f"The input '{field_name}' at {page_url} is vulnerable to "
                    f"cross-site scripting. The payload '{payload_info['name']}' was injected "
                    f"and JavaScript executed in the browser, changing the page title. "
                    f"An attacker can execute arbitrary JavaScript in victims' browsers."
                ),
                "proof_of_concept": (
                    f"Page: {page_url}\n"
                    f"Input: {field_name}\n"
                    f"Payload: {payload_info['payload']}\n\n"
                    f"Result: Page title changed to 'VALKYRIE_XSS_{marker}'\n"
                    f"Page title after submit: {page_title}"
                ),
                "remediation": (
                    "Encode all user input before rendering in HTML. Use Content-Security-Policy "
                    "headers. Implement input validation. Use framework auto-escaping features."
                ),
                "cvss_score": 9.0,
            })
            return True

        elif reflected:
            self.logger.warning(f"  HIGH: XSS payload reflected in page content!")
            self.add_vulnerability({
                "endpoint": page_url,
                "method": method,
                "vulnerability_type": "xss_reflected",
                "severity": "high",
                "title": f"Reflected XSS (HTML Injection) via '{field_name}'",
                "description": (
                    f"The input '{field_name}' at {page_url} reflects user input "
                    f"without proper sanitization. The marker was found in the rendered page. "
                    f"While JavaScript execution was not confirmed, HTML injection is possible."
                ),
                "proof_of_concept": (
                    f"Page: {page_url}\n"
                    f"Input: {field_name}\n"
                    f"Payload: {payload_info['payload']}\n\n"
                    f"Marker found in page: Yes\n"
                    f"Context: {str(marker_context)[:300]}"
                ),
                "remediation": (
                    "Encode all user input before rendering in HTML. Use Content-Security-Policy "
                    "headers. Implement input validation."
                ),
                "cvss_score": 7.5,
            })
            return True

        self.logger.info(f"  No XSS detected with {payload_info['name']}")
        return False

    def _test_search_xss(self) -> None:
        """Test the site's search bar for XSS. Single rtrvr call."""
        self.logger.info("\n[XSS - SEARCH BAR] Testing search bar for XSS...")

        marker = uuid.uuid4().hex[:8]
        payload_info = _make_payload(marker)
        payload = payload_info["payload"]
        self.logger.info(f"  Payload: {payload_info['name']}")

        task = (
            f"Go to {self.target_url}. "
            f"Find the search bar or search input. "
            f"Type this into it: {payload} "
            f"Press Enter to submit. "
            f"After the page loads, report: "
            f"1) The page title "
            f"2) Whether 'VALKYRIE_XSS_{marker}' appears in the page "
            f"3) The text around it if found"
        )

        self._rtrvr_calls += 1
        result = self._call_rtrvr(task, self.target_url)
        self._check_xss_result(result, marker, payload_info,
                                self.target_url, "search bar", "GET")

    def _test_url_param_xss(self, endpoint: str) -> None:
        """Test a URL parameter endpoint for XSS. Single rtrvr call."""
        self.logger.info(f"\n[XSS - URL PARAM] Testing endpoint: {endpoint}")

        marker = uuid.uuid4().hex[:8]
        payload_info = _make_payload(marker)
        payload = payload_info["payload"]

        # Build the full URL with payload in the query parameter
        if "?" in endpoint:
            test_url = urljoin(self.target_url, endpoint) + payload
        else:
            test_url = urljoin(self.target_url, endpoint) + f"?q={payload}"

        self.logger.info(f"  Testing URL: {test_url}")

        task = (
            f"Navigate to this exact URL: {test_url} "
            f"After the page loads, report: "
            f"1) The page title "
            f"2) Whether the text 'VALKYRIE_XSS_{marker}' appears anywhere on the page "
            f"3) What content is shown on the page"
        )

        self._rtrvr_calls += 1
        result = self._call_rtrvr(task, test_url)
        self._check_xss_result(result, marker, payload_info,
                                test_url, f"URL param ({endpoint})", "GET")

    def _test_page_form_xss(self, page_url: str, description: str, field_hint: str) -> None:
        """Test a specific page's form for XSS. Single rtrvr call."""
        self.logger.info(f"\n[XSS - FORM] Testing {description} at {page_url}")

        marker = uuid.uuid4().hex[:8]
        payload_info = _make_payload(marker)
        payload = payload_info["payload"]
        self.logger.info(f"  Payload: {payload_info['name']}")

        task = (
            f"Go to {page_url}. "
            f"Find any input field (look for one related to '{field_hint}'). "
            f"Type this into it: {payload} "
            f"Submit the form (click submit/send button or press Enter). "
            f"After the page loads, report: "
            f"1) The page title "
            f"2) Whether 'VALKYRIE_XSS_{marker}' appears in the page "
            f"3) The surrounding text if found"
        )

        self._rtrvr_calls += 1
        result = self._call_rtrvr(task, page_url)
        self._check_xss_result(result, marker, payload_info,
                                page_url, description, "POST")

    def add_vulnerability(self, vuln: Dict) -> None:
        self.vulnerabilities.append(vuln)
        self.logger.warning(f"\n{'*' * 60}")
        self.logger.warning(f"VULNERABILITY: {vuln['title']}")
        self.logger.warning(f"Severity: {vuln['severity'].upper()}")
        self.logger.warning(f"CVSS: {vuln.get('cvss_score', 'N/A')}")
        self.logger.warning(f"{'*' * 60}\n")
