"""
Unauthenticated Vulnerability Testing Engine
Tests for vulnerabilities that don't require authentication
"""

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import re
import logging
from typing import List, Dict
from urllib.parse import urlparse, urljoin


class UnauthVulnerabilityEngine:
    def __init__(self, target_url: str, logger: logging.Logger = None):
        """
        Initialize Unauthenticated Vulnerability Testing Engine

        Args:
            target_url: Target URL to test
            logger: Logger instance
        """
        self.target_url = target_url.rstrip('/')
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Valkyrie-Security-Scanner/1.0'})

        parsed = urlparse(target_url)
        self.domain = parsed.netloc
        self.scheme = parsed.scheme or 'https'
        self.base_url = f"{self.scheme}://{self.domain}"

        self.vulnerabilities = []

    def run_all_tests(self) -> List[Dict]:
        """Run all unauthenticated vulnerability tests"""

        self.logger.info("="*80)
        self.logger.info("Starting Unauthenticated Vulnerability Tests")
        self.logger.info("="*80)

        # 1. Security Headers Analysis
        self.test_security_headers()

        # 2. Information Disclosure
        self.test_information_disclosure()

        # 3. Exposed Files
        self.test_exposed_files()

        # 4. Server Fingerprinting
        self.test_server_fingerprinting()

        # 5. Cookie Security
        self.test_cookie_security()

        # 6. CORS Misconfiguration
        self.test_cors()

        self.logger.info("="*80)
        self.logger.info(f"Unauthenticated tests complete. Found {len(self.vulnerabilities)} vulnerabilities")
        self.logger.info("="*80)

        return self.vulnerabilities

    def test_security_headers(self) -> None:
        """Test for missing security headers"""
        self.logger.info("\n[SECURITY HEADERS] Testing security headers...")

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)
            headers = response.headers

            # Critical security headers to check
            required_headers = {
                'Strict-Transport-Security': {
                    'severity': 'high',
                    'description': 'HSTS header missing - site is vulnerable to SSL stripping attacks',
                    'remediation': 'Add "Strict-Transport-Security: max-age=31536000; includeSubDomains" header'
                },
                'X-Frame-Options': {
                    'severity': 'medium',
                    'description': 'X-Frame-Options header missing - site is vulnerable to clickjacking',
                    'remediation': 'Add "X-Frame-Options: DENY" or "X-Frame-Options: SAMEORIGIN" header'
                },
                'X-Content-Type-Options': {
                    'severity': 'medium',
                    'description': 'X-Content-Type-Options header missing - browsers may MIME-sniff responses',
                    'remediation': 'Add "X-Content-Type-Options: nosniff" header'
                },
                'Content-Security-Policy': {
                    'severity': 'high',
                    'description': 'Content-Security-Policy header missing - site is vulnerable to XSS',
                    'remediation': 'Implement a Content-Security-Policy that restricts resource loading'
                },
                'X-XSS-Protection': {
                    'severity': 'low',
                    'description': 'X-XSS-Protection header missing or disabled',
                    'remediation': 'Add "X-XSS-Protection: 1; mode=block" header'
                },
            }

            for header, config in required_headers.items():
                if header not in headers:
                    self.logger.warning(f"⚠️  Missing header: {header}")
                    self.add_vulnerability({
                        'vulnerability_type': 'missing_security_header',
                        'severity': config['severity'],
                        'title': f'Missing Security Header: {header}',
                        'description': config['description'],
                        'proof_of_concept': f'Request to {self.base_url} does not include {header} header',
                        'remediation': config['remediation'],
                        'endpoint': self.base_url,
                        'method': 'GET'
                    })
                else:
                    self.logger.info(f"✓ {header}: {headers[header][:50]}...")

        except Exception as e:
            self.logger.error(f"Error testing security headers: {str(e)}")

    def test_information_disclosure(self) -> None:
        """Test for information disclosure vulnerabilities"""
        self.logger.info("\n[INFORMATION DISCLOSURE] Testing for verbose errors and debug info...")

        # Test endpoints that might expose debug info
        debug_endpoints = [
            '/.env',
            '/debug',
            '/_debug',
            '/config',
            '/configuration',
            '/phpinfo.php',
            '/info.php',
            '/test.php',
            '/.git/config',
            '/.git/HEAD',
            '/server-status',
            '/server-info',
            '/.htaccess',
            '/web.config',
            '/WEB-INF/web.xml',
            '/errors',
            '/error',
            '/stacktrace',
        ]

        for endpoint in debug_endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                response = self.session.get(url, timeout=5, verify=False)

                if response.status_code == 200:
                    content = response.text.lower()

                    # Check for sensitive information
                    sensitive_patterns = {
                        'database': r'(mysql|postgres|mongodb|redis|database)',
                        'credentials': r'(password|secret|api[_-]?key|token)',
                        'paths': r'(/var/www|/home/|c:\\|/usr/)',
                        'stack_trace': r'(stack trace|traceback|exception)',
                    }

                    found_sensitive = False
                    for pattern_name, pattern in sensitive_patterns.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            found_sensitive = True
                            break

                    if found_sensitive or len(response.text) > 100:
                        self.logger.warning(f"⚠️  Exposed file: {endpoint}")
                        self.add_vulnerability({
                            'vulnerability_type': 'information_disclosure',
                            'severity': 'high',
                            'title': f'Information Disclosure: {endpoint}',
                            'description': f'Sensitive file or debug endpoint is publicly accessible',
                            'proof_of_concept': f'GET {url} returns 200 OK\n\nResponse preview:\n{response.text[:500]}...',
                            'remediation': 'Remove or restrict access to debug/configuration files',
                            'endpoint': endpoint,
                            'method': 'GET'
                        })

            except Exception as e:
                self.logger.debug(f"Endpoint {endpoint} not found: {str(e)}")

    def test_exposed_files(self) -> None:
        """Test for exposed backup files and sensitive files"""
        self.logger.info("\n[EXPOSED FILES] Testing for backup and sensitive files...")

        # Common backup file extensions and patterns
        backup_patterns = [
            '/backup.zip',
            '/backup.tar.gz',
            '/backup.sql',
            '/database.sql',
            '/db.sql',
            '/dump.sql',
            '/config.bak',
            '/config.old',
            '/.env.bak',
            '/.env.old',
            '/.env.backup',
            '/credentials.txt',
            '/passwords.txt',
            '/keys.txt',
            '/secrets.txt',
        ]

        for file_path in backup_patterns:
            try:
                url = urljoin(self.base_url, file_path)
                response = self.session.get(url, timeout=5, verify=False)

                if response.status_code == 200 and len(response.content) > 0:
                    self.logger.warning(f"⚠️  Exposed backup file: {file_path}")
                    self.add_vulnerability({
                        'vulnerability_type': 'exposed_backup_file',
                        'severity': 'critical',
                        'title': f'Exposed Backup File: {file_path}',
                        'description': 'Backup or sensitive file is publicly accessible, potentially containing credentials or sensitive data',
                        'proof_of_concept': f'GET {url} returns 200 OK\n\nFile size: {len(response.content)} bytes',
                        'remediation': 'Remove backup files from web-accessible directories or restrict access with authentication',
                        'endpoint': file_path,
                        'method': 'GET',
                        'cvss_score': 9.0
                    })

            except Exception as e:
                self.logger.debug(f"File {file_path} not found: {str(e)}")

    def test_server_fingerprinting(self) -> None:
        """Test server version and fingerprinting"""
        self.logger.info("\n[SERVER FINGERPRINTING] Fingerprinting server...")

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)
            headers = response.headers

            # Check for verbose server headers
            if 'Server' in headers:
                server = headers['Server']
                self.logger.info(f"Server: {server}")

                # Check if version is exposed
                version_pattern = r'[\d]+\.[\d]+\.[\d]+'
                if re.search(version_pattern, server):
                    self.logger.warning(f"⚠️  Server version exposed: {server}")
                    self.add_vulnerability({
                        'vulnerability_type': 'server_version_disclosure',
                        'severity': 'low',
                        'title': 'Server Version Disclosure',
                        'description': f'Server version is exposed in headers: {server}',
                        'proof_of_concept': f'Server header: {server}',
                        'remediation': 'Configure server to hide version information',
                        'endpoint': self.base_url,
                        'method': 'GET',
                        'cvss_score': 3.0
                    })

            # Check for X-Powered-By header
            if 'X-Powered-By' in headers:
                powered_by = headers['X-Powered-By']
                self.logger.warning(f"⚠️  X-Powered-By header exposed: {powered_by}")
                self.add_vulnerability({
                    'vulnerability_type': 'technology_disclosure',
                    'severity': 'low',
                    'title': 'Technology Disclosure',
                    'description': f'X-Powered-By header reveals technology stack: {powered_by}',
                    'proof_of_concept': f'X-Powered-By header: {powered_by}',
                    'remediation': 'Remove X-Powered-By header from responses',
                    'endpoint': self.base_url,
                    'method': 'GET',
                    'cvss_score': 2.0
                    })

        except Exception as e:
            self.logger.error(f"Error fingerprinting server: {str(e)}")

    def test_cookie_security(self) -> None:
        """Test cookie security flags"""
        self.logger.info("\n[COOKIE SECURITY] Testing cookie security...")

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)

            if 'Set-Cookie' in response.headers or response.cookies:
                self.logger.info("Cookies detected, analyzing...")

                for cookie in response.cookies:
                    cookie_issues = []

                    # Check HttpOnly flag
                    if not cookie.has_nonstandard_attr('HttpOnly'):
                        cookie_issues.append('missing HttpOnly flag')

                    # Check Secure flag
                    if not cookie.secure and self.scheme == 'https':
                        cookie_issues.append('missing Secure flag')

                    # Check SameSite attribute
                    if not cookie.has_nonstandard_attr('SameSite'):
                        cookie_issues.append('missing SameSite attribute')

                    if cookie_issues:
                        self.logger.warning(f"⚠️  Cookie '{cookie.name}' has issues: {', '.join(cookie_issues)}")
                        self.add_vulnerability({
                            'vulnerability_type': 'insecure_cookie',
                            'severity': 'medium',
                            'title': f'Insecure Cookie Configuration: {cookie.name}',
                            'description': f"Cookie '{cookie.name}' is missing security flags: {', '.join(cookie_issues)}",
                            'proof_of_concept': f'Set-Cookie header for {cookie.name} does not include proper security attributes',
                            'remediation': 'Set HttpOnly, Secure, and SameSite attributes on all cookies',
                            'endpoint': self.base_url,
                            'method': 'GET',
                            'cvss_score': 5.0
                        })
            else:
                self.logger.info("No cookies detected")

        except Exception as e:
            self.logger.error(f"Error testing cookies: {str(e)}")

    def test_cors(self) -> None:
        """Test for CORS misconfiguration"""
        self.logger.info("\n[CORS] Testing CORS configuration...")

        try:
            # Test with a malicious origin
            malicious_origin = 'https://evil.com'
            headers = {'Origin': malicious_origin}

            response = self.session.get(self.base_url, headers=headers, timeout=10, verify=False)

            if 'Access-Control-Allow-Origin' in response.headers:
                allowed_origin = response.headers['Access-Control-Allow-Origin']

                # Check for wildcard
                if allowed_origin == '*':
                    self.logger.warning(f"⚠️  CORS allows all origins: {allowed_origin}")
                    self.add_vulnerability({
                        'vulnerability_type': 'cors_misconfiguration',
                        'severity': 'medium',
                        'title': 'CORS Misconfiguration: Wildcard Origin',
                        'description': 'CORS is configured to allow requests from any origin (*)',
                        'proof_of_concept': f'Access-Control-Allow-Origin: {allowed_origin}',
                        'remediation': 'Configure CORS to allow only trusted origins, not wildcard (*)',
                        'endpoint': self.base_url,
                        'method': 'GET',
                        'cvss_score': 5.5
                    })

                # Check if it reflects the malicious origin
                elif allowed_origin == malicious_origin:
                    self.logger.warning(f"⚠️  CORS reflects arbitrary origins")
                    self.add_vulnerability({
                        'vulnerability_type': 'cors_misconfiguration',
                        'severity': 'high',
                        'title': 'CORS Misconfiguration: Origin Reflection',
                        'description': 'CORS reflects arbitrary origins without validation',
                        'proof_of_concept': f'Sent Origin: {malicious_origin}\nReceived Access-Control-Allow-Origin: {allowed_origin}',
                        'remediation': 'Implement proper origin validation in CORS configuration',
                        'endpoint': self.base_url,
                        'method': 'GET',
                        'cvss_score': 7.0
                    })
                else:
                    self.logger.info(f"✓ CORS properly configured: {allowed_origin}")

        except Exception as e:
            self.logger.error(f"Error testing CORS: {str(e)}")

    def add_vulnerability(self, vuln: Dict) -> None:
        """Add a vulnerability to the list"""
        self.vulnerabilities.append(vuln)
        self.logger.warning(f"\n{'*'*60}")
        self.logger.warning(f"VULNERABILITY: {vuln['title']}")
        self.logger.warning(f"Severity: {vuln['severity'].upper()}")
        self.logger.warning(f"{'*'*60}\n")
