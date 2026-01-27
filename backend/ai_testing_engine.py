"""
AI-Powered Smart Testing Engine
Uses intelligent analysis, pattern recognition, and context-aware testing
"""

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import re
import json
import logging
from typing import List, Dict, Set, Any, Optional
from urllib.parse import urlparse, urljoin, parse_qs, urlunparse
from collections import defaultdict
import itertools
from testing_utils import get_allowed_methods, is_readonly_resource, is_public_endpoint


class AITestingEngine:
    def __init__(self, target_url: str, logger: logging.Logger = None):
        """
        Initialize AI-Powered Testing Engine

        Args:
            target_url: Target URL to test
            logger: Logger instance
        """
        self.target_url = target_url.rstrip('/')
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Valkyrie-AI-Scanner/1.0'})

        parsed = urlparse(target_url)
        self.domain = parsed.netloc
        self.scheme = parsed.scheme or 'https'
        self.base_url = f"{self.scheme}://{self.domain}"

        self.discovered_endpoints: Set[str] = set()
        self.response_patterns: Dict[str, Any] = {}
        self.vulnerabilities = []

    def run_all_ai_tests(self, known_endpoints: List[str] = None) -> Dict:
        """Run all AI-powered tests"""

        self.logger.info("="*80)
        self.logger.info("Starting AI-Powered Smart Testing")
        self.logger.info("="*80)

        known_endpoints = known_endpoints or []

        # 1. Smart Endpoint Prediction
        predicted_endpoints = self.predict_endpoints(known_endpoints)

        # 2. Response Pattern Analysis
        self.analyze_response_patterns(known_endpoints + list(predicted_endpoints))

        # 3. Context-Aware Payload Generation & Testing
        self.test_with_smart_payloads(known_endpoints)

        # 4. Behavioral Analysis
        self.behavioral_analysis()

        # 5. Error-Based Information Disclosure
        self.test_error_based_disclosure()

        self.logger.info("="*80)
        self.logger.info(f"AI Testing complete! Found {len(self.vulnerabilities)} vulnerabilities")
        self.logger.info(f"Predicted {len(predicted_endpoints)} new endpoints")
        self.logger.info("="*80)

        return {
            'vulnerabilities': self.vulnerabilities,
            'predicted_endpoints': list(predicted_endpoints),
            'response_patterns': self.response_patterns,
        }

    def predict_endpoints(self, known_endpoints: List[str]) -> Set[str]:
        """
        AI-powered endpoint prediction based on patterns
        Analyzes known endpoints to predict likely variations
        """
        self.logger.info("\n[AI ENDPOINT PREDICTION] Analyzing patterns...")

        predicted = set()

        if not known_endpoints:
            # If no known endpoints, predict common patterns
            base_resources = ['users', 'accounts', 'products', 'items', 'orders',
                            'customers', 'posts', 'comments', 'data', 'files']

            for resource in base_resources:
                predicted.update([
                    f'/api/{resource}',
                    f'/api/v1/{resource}',
                    f'/api/v2/{resource}',
                    f'/{resource}',
                ])
        else:
            # Analyze patterns in known endpoints
            patterns = self._extract_patterns(known_endpoints)

            # Predict variations
            for pattern in patterns:
                predicted.update(self._generate_variations(pattern))

        # Test predicted endpoints
        verified = set()
        for endpoint in list(predicted)[:20]:  # Limit to avoid too many requests
            try:
                url = urljoin(self.base_url, endpoint)
                response = self.session.get(url, timeout=5, verify=False, allow_redirects=False)

                if response.status_code in [200, 201, 401, 403, 405]:
                    verified.add(endpoint)
                    self.logger.info(f"✓ Predicted endpoint exists: {endpoint} [{response.status_code}]")

            except Exception as e:
                self.logger.debug(f"Predicted endpoint {endpoint} not found: {str(e)}")

        self.discovered_endpoints.update(verified)
        return verified

    def _extract_patterns(self, endpoints: List[str]) -> List[Dict]:
        """Extract patterns from known endpoints"""
        patterns = []

        for endpoint in endpoints:
            parts = [p for p in endpoint.split('/') if p]

            pattern = {
                'parts': parts,
                'has_id': any(p.isdigit() or '{' in p for p in parts),
                'depth': len(parts),
                'prefix': parts[0] if parts else None,
            }
            patterns.append(pattern)

        return patterns

    def _generate_variations(self, pattern: Dict) -> Set[str]:
        """Generate endpoint variations based on pattern"""
        variations = set()
        parts = pattern['parts']

        if not parts:
            return variations

        # Version variations
        if 'api' in parts:
            for version in ['v1', 'v2', 'v3']:
                new_parts = parts.copy()
                if 'v1' in new_parts:
                    idx = new_parts.index('v1')
                    new_parts[idx] = version
                else:
                    new_parts.insert(1, version)
                variations.add('/' + '/'.join(new_parts))

        # Resource variations (singular/plural)
        for i, part in enumerate(parts):
            if part.endswith('s'):
                # Try singular
                new_parts = parts.copy()
                new_parts[i] = part[:-1]
                variations.add('/' + '/'.join(new_parts))
            else:
                # Try plural
                new_parts = parts.copy()
                new_parts[i] = part + 's'
                variations.add('/' + '/'.join(new_parts))

        # ID variations
        if pattern['has_id']:
            for i, part in enumerate(parts):
                if part.isdigit() or '{' in part:
                    for test_id in ['1', '123', 'me', 'self', 'current']:
                        new_parts = parts.copy()
                        new_parts[i] = test_id
                        variations.add('/' + '/'.join(new_parts))

        # Sub-resource predictions
        common_sub_resources = ['settings', 'profile', 'permissions', 'history',
                               'details', 'info', 'status', 'metadata']

        for sub in common_sub_resources:
            variations.add('/' + '/'.join(parts) + f'/{sub}')

        return variations

    def analyze_response_patterns(self, endpoints: List[str]) -> None:
        """
        Analyze response patterns to detect anomalies and security issues
        """
        self.logger.info("\n[AI RESPONSE ANALYSIS] Analyzing response patterns...")

        response_data = []

        for endpoint in endpoints[:15]:  # Limit to avoid too many requests
            try:
                url = urljoin(self.base_url, endpoint)

                # Get allowed methods for this endpoint (skip write methods on read-only resources)
                allowed_methods = get_allowed_methods(endpoint)

                # Log if we're restricting methods for this endpoint
                if is_readonly_resource(endpoint) or is_public_endpoint(endpoint):
                    self.logger.info(f"ℹ️  Testing {endpoint} with limited methods: {allowed_methods}")

                # Test with allowed methods only
                for method in allowed_methods:
                    try:
                        response = self.session.request(method, url, timeout=5, verify=False)

                        response_data.append({
                            'endpoint': endpoint,
                            'method': method,
                            'status': response.status_code,
                            'length': len(response.content),
                            'headers': dict(response.headers),
                            'response_time': response.elapsed.total_seconds(),
                        })

                    except Exception as e:
                        self.logger.debug(f"Method {method} failed on {endpoint}: {str(e)}")

            except Exception as e:
                self.logger.debug(f"Failed to analyze {endpoint}: {str(e)}")

        # Analyze patterns
        self._detect_anomalies(response_data)

        # Store patterns
        self.response_patterns = {
            'total_tested': len(response_data),
            'status_distribution': self._get_status_distribution(response_data),
            'avg_response_time': sum(r['response_time'] for r in response_data) / len(response_data) if response_data else 0,
        }

        self.logger.info(f"Analyzed {len(response_data)} responses")
        self.logger.info(f"Average response time: {self.response_patterns['avg_response_time']:.3f}s")

    def _detect_anomalies(self, response_data: List[Dict]) -> None:
        """Detect anomalies in response patterns"""

        # Check for methods that should be restricted but aren't
        for data in response_data:
            if data['method'] in ['PUT', 'DELETE'] and data['status'] == 200:
                # Skip if this is a read-only resource (XML, TXT, etc.)
                if is_readonly_resource(data['endpoint']):
                    self.logger.info(f"ℹ️  Skipping {data['method']} test on read-only resource: {data['endpoint']}")
                    continue

                # Skip if this is a public endpoint (sitemaps, robots.txt, etc.)
                if is_public_endpoint(data['endpoint']):
                    self.logger.info(f"ℹ️  Skipping {data['method']} test on public endpoint: {data['endpoint']}")
                    continue

                self.logger.warning(f"⚠️  Unrestricted {data['method']} method on {data['endpoint']}")
                self.add_vulnerability({
                    'vulnerability_type': 'unrestricted_http_method',
                    'severity': 'high',
                    'title': f"Unrestricted HTTP Method: {data['method']}",
                    'description': f"{data['method']} method is accessible without proper restrictions on {data['endpoint']}",
                    'proof_of_concept': f"{data['method']} {data['endpoint']} returns {data['status']}",
                    'remediation': f"Restrict {data['method']} method to authenticated and authorized users only",
                    'endpoint': data['endpoint'],
                    'method': data['method'],
                    'cvss_score': 7.5
                })

        # Check for verbose error messages
        for data in response_data:
            if data['status'] >= 500:
                self.logger.warning(f"⚠️  Server error on {data['endpoint']}: {data['status']}")
                # This might indicate information disclosure

    def _get_status_distribution(self, response_data: List[Dict]) -> Dict:
        """Get distribution of status codes"""
        distribution = defaultdict(int)
        for data in response_data:
            distribution[data['status']] += 1
        return dict(distribution)

    def test_with_smart_payloads(self, endpoints: List[str]) -> None:
        """
        Generate and test with context-aware smart payloads
        """
        self.logger.info("\n[AI SMART PAYLOADS] Testing with intelligent payloads...")

        for endpoint in endpoints[:10]:  # Limit testing
            try:
                url = urljoin(self.base_url, endpoint)

                # Analyze endpoint to determine appropriate payloads
                payloads = self._generate_smart_payloads(endpoint)

                for payload_type, payload in payloads.items():
                    self._test_payload(url, payload_type, payload)

            except Exception as e:
                self.logger.debug(f"Payload testing failed on {endpoint}: {str(e)}")

    def _generate_smart_payloads(self, endpoint: str) -> Dict[str, Any]:
        """Generate context-aware payloads based on endpoint"""
        payloads = {}

        # Identify resource type
        if 'user' in endpoint.lower():
            payloads['privilege_escalation'] = {
                'role': 'admin',
                'is_admin': True,
                'admin': True,
                'privileges': ['admin', 'superuser'],
            }
            payloads['account_takeover'] = {
                'email': 'attacker@evil.com',
                'password': 'hacked123',
            }

        if 'product' in endpoint.lower() or 'item' in endpoint.lower():
            payloads['price_manipulation'] = {
                'price': 0.01,
                'discount': 100,
                'cost': -1,
            }

        if 'order' in endpoint.lower():
            payloads['order_manipulation'] = {
                'status': 'completed',
                'paid': True,
                'amount': 0,
            }

        # Generic payloads for any endpoint
        payloads['mass_assignment'] = {
            'id': 1,
            'user_id': 1,
            'admin': True,
            'role': 'admin',
            'verified': True,
            'active': True,
        }

        payloads['sql_injection'] = {
            'id': "1' OR '1'='1",
            'search': "'; DROP TABLE users--",
        }

        payloads['xss'] = {
            'name': '<script>alert(1)</script>',
            'comment': '<img src=x onerror=alert(1)>',
        }

        payloads['command_injection'] = {
            'file': '../../etc/passwd',
            'path': '../../../etc/hosts',
            'url': 'file:///etc/passwd',
        }

        return payloads

    def _test_payload(self, url: str, payload_type: str, payload: Dict) -> None:
        """Test a specific payload"""
        try:
            # Test POST
            response = self.session.post(url, json=payload, timeout=5, verify=False)
            self._analyze_payload_response(url, 'POST', payload_type, payload, response)

            # Test PUT
            response = self.session.put(url, json=payload, timeout=5, verify=False)
            self._analyze_payload_response(url, 'PUT', payload_type, payload, response)

        except Exception as e:
            self.logger.debug(f"Payload test failed: {str(e)}")

    def _analyze_payload_response(self, url: str, method: str, payload_type: str,
                                  payload: Dict, response: requests.Response) -> None:
        """Analyze response to payload"""

        # Check if payload was reflected (potential XSS)
        if payload_type == 'xss':
            for key, value in payload.items():
                if value in response.text:
                    self.logger.warning(f"⚠️  Reflected XSS payload in response")
                    self.add_vulnerability({
                        'vulnerability_type': 'reflected_xss',
                        'severity': 'high',
                        'title': 'Potential Reflected XSS',
                        'description': f'XSS payload was reflected in response without encoding',
                        'proof_of_concept': f'{method} {url}\nPayload: {json.dumps(payload)}\n\nPayload reflected in response',
                        'remediation': 'Implement proper input validation and output encoding',
                        'endpoint': url,
                        'method': method,
                        'cvss_score': 7.0
                    })

        # Check for SQL errors (potential SQLi)
        if payload_type == 'sql_injection':
            sql_errors = [
                'sql syntax', 'mysql', 'postgresql', 'sqlite', 'oracle',
                'syntax error', 'database error', 'query failed'
            ]
            response_lower = response.text.lower()

            for error in sql_errors:
                if error in response_lower:
                    self.logger.warning(f"⚠️  SQL error detected in response")
                    self.add_vulnerability({
                        'vulnerability_type': 'sql_injection',
                        'severity': 'critical',
                        'title': 'Potential SQL Injection',
                        'description': f'SQL error message detected in response, indicating possible SQL injection',
                        'proof_of_concept': f'{method} {url}\nPayload: {json.dumps(payload)}\n\nSQL error in response',
                        'remediation': 'Use parameterized queries and input validation',
                        'endpoint': url,
                        'method': method,
                        'cvss_score': 9.0
                    })
                    break

        # Check for path traversal success
        if payload_type == 'command_injection':
            indicators = ['root:', '/bin/', '/etc/', 'localhost', '127.0.0.1']

            for indicator in indicators:
                if indicator in response.text:
                    self.logger.warning(f"⚠️  Potential path traversal/command injection")
                    self.add_vulnerability({
                        'vulnerability_type': 'path_traversal',
                        'severity': 'critical',
                        'title': 'Potential Path Traversal/Command Injection',
                        'description': f'System file content detected in response',
                        'proof_of_concept': f'{method} {url}\nPayload: {json.dumps(payload)}\n\nSystem indicator found: {indicator}',
                        'remediation': 'Implement strict input validation and use allowlists',
                        'endpoint': url,
                        'method': method,
                        'cvss_score': 9.5
                    })
                    break

    def behavioral_analysis(self) -> None:
        """
        Analyze API behavior patterns
        """
        self.logger.info("\n[AI BEHAVIORAL ANALYSIS] Analyzing API behavior...")

        # Test timing attacks
        self._test_timing_attacks()

        # Test response size variations
        self._test_response_variations()

    def _test_timing_attacks(self) -> None:
        """Test for timing-based information disclosure"""
        self.logger.info("Testing for timing-based vulnerabilities...")

        try:
            # Test login endpoint timing
            login_paths = ['/login', '/api/login', '/auth/login', '/api/auth/login']

            for path in login_paths:
                url = urljoin(self.base_url, path)

                # Test with valid-looking vs invalid usernames
                valid_times = []
                invalid_times = []

                for _ in range(3):
                    # Valid format username
                    start = time.time()
                    try:
                        self.session.post(url, json={'username': 'admin', 'password': 'wrong'},
                                        timeout=5, verify=False)
                    except:
                        pass
                    valid_times.append(time.time() - start)

                    # Invalid format username
                    start = time.time()
                    try:
                        self.session.post(url, json={'username': 'x', 'password': 'wrong'},
                                        timeout=5, verify=False)
                    except:
                        pass
                    invalid_times.append(time.time() - start)

                # Compare average times
                if valid_times and invalid_times:
                    avg_valid = sum(valid_times) / len(valid_times)
                    avg_invalid = sum(invalid_times) / len(invalid_times)

                    # If there's significant timing difference
                    if abs(avg_valid - avg_invalid) > 0.5:  # 500ms difference
                        self.logger.warning(f"⚠️  Timing attack vulnerability detected on {path}")
                        self.add_vulnerability({
                            'vulnerability_type': 'timing_attack',
                            'severity': 'medium',
                            'title': 'Timing Attack Vulnerability',
                            'description': f'Login endpoint reveals user existence through response timing differences',
                            'proof_of_concept': f'Valid username avg time: {avg_valid:.3f}s\nInvalid username avg time: {avg_invalid:.3f}s\nDifference: {abs(avg_valid - avg_invalid):.3f}s',
                            'remediation': 'Implement constant-time authentication checks',
                            'endpoint': path,
                            'method': 'POST',
                            'cvss_score': 5.0
                        })

        except Exception as e:
            self.logger.debug(f"Timing attack test failed: {str(e)}")

    def _test_response_variations(self) -> None:
        """Test for information disclosure through response variations"""
        self.logger.info("Testing response size variations...")

        # This can reveal information about resources
        pass

    def test_error_based_disclosure(self) -> None:
        """
        Test for information disclosure through error messages
        """
        self.logger.info("\n[AI ERROR ANALYSIS] Testing error-based disclosure...")

        # Send malformed requests to trigger errors
        test_cases = [
            {'data': '{"invalid": json}', 'content_type': 'application/json'},
            {'data': '<xml>invalid</xml>', 'content_type': 'application/xml'},
            {'data': 'invalid_data', 'content_type': 'application/json'},
        ]

        for test_case in test_cases:
            try:
                response = self.session.post(
                    self.base_url,
                    data=test_case['data'],
                    headers={'Content-Type': test_case['content_type']},
                    timeout=5,
                    verify=False
                )

                # Check for verbose error messages
                sensitive_info = [
                    'traceback', 'stack trace', 'exception',
                    '/home/', '/var/', 'c:\\',
                    'line ', 'file ', 'function ',
                    'mysql', 'postgresql', 'mongodb',
                ]

                response_lower = response.text.lower()
                for info in sensitive_info:
                    if info in response_lower:
                        self.logger.warning(f"⚠️  Verbose error message detected")
                        self.add_vulnerability({
                            'vulnerability_type': 'verbose_error',
                            'severity': 'low',
                            'title': 'Verbose Error Messages',
                            'description': 'Application returns detailed error messages that may reveal system information',
                            'proof_of_concept': f'Malformed request triggers verbose error containing: {info}',
                            'remediation': 'Configure application to return generic error messages in production',
                            'endpoint': self.base_url,
                            'method': 'POST',
                            'cvss_score': 3.0
                        })
                        break

            except Exception as e:
                self.logger.debug(f"Error disclosure test failed: {str(e)}")

    def add_vulnerability(self, vuln: Dict) -> None:
        """Add a vulnerability to the list"""
        self.vulnerabilities.append(vuln)
        self.logger.warning(f"\n{'*'*60}")
        self.logger.warning(f"VULNERABILITY: {vuln['title']}")
        self.logger.warning(f"Severity: {vuln['severity'].upper()}")
        self.logger.warning(f"{'*'*60}\n")


import time
