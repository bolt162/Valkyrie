"""
API Security Testing Engine
Tests APIs for common vulnerabilities: JWT, BOLA, Authentication, Rate Limiting, Mass Assignment
"""

import requests
import jwt
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
from urllib.parse import urlparse, urljoin
from unauth_vuln_engine import UnauthVulnerabilityEngine
from fuzzing_engine import FuzzingEngine
from ai_testing_engine import AITestingEngine
from network_testing_engine import NetworkTestingEngine
from testing_utils import should_skip_auth_test, is_public_endpoint, get_endpoint_classification

class ApiSecurityEngine:
    def __init__(self, target_url: str, auth_config: Dict = None, logger: logging.Logger = None):
        """
        Initialize API Security Engine

        Args:
            target_url: Base URL of the API to test
            auth_config: Authentication configuration {type, credentials}
            logger: Logger instance for detailed logging
        """
        self.target_url = target_url.rstrip('/')
        self.auth_config = auth_config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.vulnerabilities = []
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Valkyrie-Security-Scanner/1.0'})

    def setup_authentication(self) -> Dict[str, str]:
        """Setup authentication headers based on auth_config"""
        headers = {}

        auth_type = self.auth_config.get('type', 'none')
        creds = self.auth_config.get('credentials', {})

        if auth_type == 'bearer':
            token = creds.get('token', '')
            headers['Authorization'] = f'Bearer {token}'
        elif auth_type == 'api_key':
            key_name = creds.get('key_name', 'X-API-Key')
            key_value = creds.get('key_value', '')
            headers[key_name] = key_value
        elif auth_type == 'basic':
            import base64
            username = creds.get('username', '')
            password = creds.get('password', '')
            credentials = f"{username}:{password}".encode('utf-8')
            encoded = base64.b64encode(credentials).decode('utf-8')
            headers['Authorization'] = f'Basic {encoded}'

        return headers

    def run_all_tests(self, endpoints: List[str], test_types: List[str]) -> List[Dict]:
        """
        Run all requested security tests

        Args:
            endpoints: List of endpoint paths to test
            test_types: List of test types to run ['jwt', 'bola', 'auth', 'rate_limit', 'mass_assignment', 'unauth']

        Returns:
            List of vulnerabilities found
        """
        self.logger.info(f"Starting API security tests on {self.target_url}")
        self.logger.info(f"Testing {len(endpoints)} endpoints with test types: {test_types}")

        # Run unauthenticated tests first (they don't require endpoints or auth)
        if 'unauth' in test_types or 'all' in test_types:
            self.logger.info("\n" + "="*60)
            self.logger.info("RUNNING UNAUTHENTICATED VULNERABILITY TESTS")
            self.logger.info("="*60)

            unauth_engine = UnauthVulnerabilityEngine(self.target_url, self.logger)
            unauth_vulns = unauth_engine.run_all_tests()
            self.vulnerabilities.extend(unauth_vulns)

        # Run fuzzing and discovery tests (they also work without endpoints or auth)
        if 'fuzzing' in test_types or 'all' in test_types:
            self.logger.info("\n" + "="*60)
            self.logger.info("RUNNING SMART FUZZING & DISCOVERY TESTS")
            self.logger.info("="*60)

            fuzzing_engine = FuzzingEngine(self.target_url, self.logger)
            fuzzing_results = fuzzing_engine.run_all_fuzzing()
            self.vulnerabilities.extend(fuzzing_results['vulnerabilities'])

            self.logger.info(f"\nDiscovered {len(fuzzing_results['discovered_paths'])} paths during fuzzing")
            self.logger.info(f"Found {len(fuzzing_results['discovered_parameters'])} parameters")

        # Run AI-powered intelligent tests
        if 'ai_testing' in test_types or 'all' in test_types:
            self.logger.info("\n" + "="*60)
            self.logger.info("RUNNING AI-POWERED SMART TESTING")
            self.logger.info("="*60)

            ai_engine = AITestingEngine(self.target_url, self.logger)
            ai_results = ai_engine.run_all_ai_tests(known_endpoints=endpoints)
            self.vulnerabilities.extend(ai_results['vulnerabilities'])

            self.logger.info(f"\nAI predicted {len(ai_results['predicted_endpoints'])} new endpoints")
            self.logger.info(f"Found {len(ai_results['vulnerabilities'])} vulnerabilities through AI analysis")

        # Run network-level tests (port scanning, service detection, WAF/CDN)
        if 'network' in test_types or 'all' in test_types:
            self.logger.info("\n" + "="*60)
            self.logger.info("RUNNING NETWORK-LEVEL TESTING")
            self.logger.info("="*60)

            network_engine = NetworkTestingEngine(self.target_url, self.logger)
            network_results = network_engine.run_all_network_tests()
            self.vulnerabilities.extend(network_results['vulnerabilities'])

            self.logger.info(f"\nFound {len(network_results['open_ports'])} open ports")
            self.logger.info(f"Service info: {network_results['service_info']}")

        auth_headers = self.setup_authentication()

        for endpoint in endpoints:
            full_url = urljoin(self.target_url, endpoint)
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Testing endpoint: {endpoint}")
            self.logger.info(f"{'='*60}")

            # Check if this is a public endpoint
            classification = get_endpoint_classification(endpoint)

            if classification['is_public']:
                self.logger.info(f"ℹ️  Endpoint identified as PUBLIC (SEO/static) - skipping auth tests")
                self.logger.info(f"   Reason: {endpoint} matches public endpoint patterns")
                # Only test rate limiting for public endpoints
                if 'rate_limit' in test_types:
                    self.test_rate_limiting(full_url, auth_headers)
                continue

            # Run requested tests (only for non-public endpoints)
            if 'jwt' in test_types:
                self.test_jwt_vulnerabilities(full_url, auth_headers)

            if 'bola' in test_types:
                self.test_bola(full_url, auth_headers)

            if 'auth' in test_types:
                self.test_authentication(full_url, auth_headers)

            if 'rate_limit' in test_types:
                self.test_rate_limiting(full_url, auth_headers)

            if 'mass_assignment' in test_types:
                self.test_mass_assignment(full_url, auth_headers)

        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Testing completed. Found {len(self.vulnerabilities)} vulnerabilities")
        self.logger.info(f"{'='*60}\n")

        return self.vulnerabilities

    def test_jwt_vulnerabilities(self, url: str, auth_headers: Dict) -> None:
        """Test for JWT-related vulnerabilities"""
        self.logger.info("\n[JWT TESTING] Starting JWT vulnerability tests")

        # Check if we have a JWT token
        auth_header = auth_headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self.logger.info("No JWT token found in authorization, skipping JWT tests")
            return

        token = auth_header.replace('Bearer ', '')

        # Test 1: None Algorithm
        self.logger.info("\n[JWT TEST 1] Testing 'none' algorithm acceptance")
        try:
            # Decode without verification to get payload
            decoded = jwt.decode(token, options={"verify_signature": False})
            self.logger.info(f"Original JWT payload: {json.dumps(decoded, indent=2)}")

            # Create token with 'none' algorithm
            none_token = jwt.encode(decoded, key="", algorithm="none")
            self.logger.info(f"Created 'none' algorithm token: {none_token[:50]}...")

            # Test if API accepts it
            test_headers = auth_headers.copy()
            test_headers['Authorization'] = f'Bearer {none_token}'

            response = requests.get(url, headers=test_headers, timeout=10)
            self.logger.info(f"Response status: {response.status_code}")

            if response.status_code == 200:
                self.logger.warning("⚠️  VULNERABILITY FOUND: API accepts 'none' algorithm JWT!")
                self.add_vulnerability({
                    'endpoint': url,
                    'method': 'GET',
                    'vulnerability_type': 'jwt_none_algorithm',
                    'severity': 'critical',
                    'title': 'JWT None Algorithm Accepted',
                    'description': 'The API accepts JWT tokens with the "none" algorithm, allowing attackers to bypass signature verification.',
                    'proof_of_concept': f'Modified JWT token with "none" algorithm:\n{none_token}\n\nResponse: {response.status_code}',
                    'remediation': 'Reject JWT tokens with "none" algorithm. Always verify JWT signatures.',
                    'cvss_score': 9.8
                })
            else:
                self.logger.info("✓ API correctly rejects 'none' algorithm tokens")

        except Exception as e:
            self.logger.error(f"Error testing JWT none algorithm: {str(e)}")

        # Test 2: Weak Secret Brute Force
        self.logger.info("\n[JWT TEST 2] Testing for weak JWT secrets")
        common_secrets = [
            "secret", "password", "123456", "key", "jwt_secret",
            "your-256-bit-secret", "mysecret", "changeme"
        ]

        for secret in common_secrets:
            try:
                decoded = jwt.decode(token, secret, algorithms=["HS256"])
                self.logger.warning(f"⚠️  VULNERABILITY FOUND: JWT secret is weak: '{secret}'")
                self.add_vulnerability({
                    'endpoint': url,
                    'method': 'GET',
                    'vulnerability_type': 'jwt_weak_secret',
                    'severity': 'critical',
                    'title': 'JWT Weak Secret Key',
                    'description': f'The JWT signing secret is weak and easily guessable: "{secret}"',
                    'proof_of_concept': f'JWT token can be decoded with secret: "{secret}"\nPayload: {json.dumps(decoded, indent=2)}',
                    'remediation': 'Use a strong, randomly generated secret key (at least 256 bits). Store it securely.',
                    'cvss_score': 9.1
                })
                return  # Found the secret, no need to continue
            except jwt.InvalidSignatureError:
                continue
            except Exception as e:
                self.logger.debug(f"Secret '{secret}' failed: {str(e)}")

        self.logger.info("✓ JWT secret appears to be strong")

        # Test 3: Missing Expiration
        self.logger.info("\n[JWT TEST 3] Checking for JWT expiration")
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            if 'exp' not in decoded:
                self.logger.warning("⚠️  VULNERABILITY FOUND: JWT has no expiration!")
                self.add_vulnerability({
                    'endpoint': url,
                    'method': 'GET',
                    'vulnerability_type': 'jwt_no_expiration',
                    'severity': 'high',
                    'title': 'JWT Missing Expiration',
                    'description': 'The JWT token does not have an expiration time (exp claim), making it valid indefinitely.',
                    'proof_of_concept': f'JWT payload: {json.dumps(decoded, indent=2)}\nNo "exp" claim found.',
                    'remediation': 'Add expiration (exp) claim to all JWT tokens. Use short expiration times (e.g., 15-60 minutes).',
                    'cvss_score': 7.5
                })
            else:
                exp_time = datetime.fromtimestamp(decoded['exp'])
                self.logger.info(f"✓ JWT has expiration: {exp_time}")
        except Exception as e:
            self.logger.error(f"Error checking JWT expiration: {str(e)}")

    def test_bola(self, url: str, auth_headers: Dict) -> None:
        """Test for Broken Object Level Authorization (BOLA/IDOR)"""
        self.logger.info("\n[BOLA TESTING] Starting BOLA/IDOR tests")

        # Extract numeric IDs from URL
        id_matches = re.findall(r'/(\d+)/?', url)

        if not id_matches:
            self.logger.info("No numeric IDs found in URL, skipping BOLA tests")
            return

        original_id = int(id_matches[-1])  # Get the last ID in URL
        self.logger.info(f"Found ID in URL: {original_id}")

        # Test with different IDs
        test_ids = [
            original_id + 1,
            original_id - 1,
            1,
            9999,
            original_id + 100
        ]

        for test_id in test_ids:
            test_url = url.replace(f'/{original_id}', f'/{test_id}')
            self.logger.info(f"\n[BOLA TEST] Testing with ID: {test_id}")
            self.logger.info(f"Test URL: {test_url}")

            try:
                response = requests.get(test_url, headers=auth_headers, timeout=10)
                self.logger.info(f"Response status: {response.status_code}")

                if response.status_code == 200:
                    self.logger.warning(f"⚠️  VULNERABILITY FOUND: Can access resource with ID {test_id}!")

                    try:
                        response_data = response.json()
                        self.logger.info(f"Response data: {json.dumps(response_data, indent=2)[:500]}...")
                    except:
                        response_data = response.text[:500]

                    self.add_vulnerability({
                        'endpoint': url,
                        'method': 'GET',
                        'vulnerability_type': 'bola_idor',
                        'severity': 'high',
                        'title': 'Broken Object Level Authorization (BOLA)',
                        'description': f'User can access other users\' resources by manipulating IDs. Successfully accessed resource with ID {test_id}.',
                        'proof_of_concept': f'Original URL: {url}\nTest URL: {test_url}\n\nResponse ({response.status_code}):\n{str(response_data)[:500]}...',
                        'remediation': 'Implement proper authorization checks. Verify that the authenticated user has permission to access the requested resource.',
                        'cvss_score': 8.2
                    })
                    break  # Found one, that's enough
                else:
                    self.logger.info(f"✓ Correctly rejected access to ID {test_id} (status: {response.status_code})")

            except Exception as e:
                self.logger.error(f"Error testing BOLA with ID {test_id}: {str(e)}")

        if not any(v['vulnerability_type'] == 'bola_idor' and v['endpoint'] == url for v in self.vulnerabilities):
            self.logger.info("✓ No BOLA vulnerabilities detected")

    def test_authentication(self, url: str, auth_headers: Dict) -> None:
        """Test authentication and authorization"""
        self.logger.info("\n[AUTH TESTING] Testing authentication and authorization")

        # Test 1: No Authentication
        self.logger.info("\n[AUTH TEST 1] Testing access without authentication")
        try:
            response = requests.get(url, timeout=10)
            self.logger.info(f"Response status without auth: {response.status_code}")

            if response.status_code == 200:
                self.logger.warning("⚠️  VULNERABILITY FOUND: Endpoint accessible without authentication!")
                self.add_vulnerability({
                    'endpoint': url,
                    'method': 'GET',
                    'vulnerability_type': 'missing_authentication',
                    'severity': 'high',
                    'title': 'Missing Authentication',
                    'description': 'The endpoint is accessible without any authentication.',
                    'proof_of_concept': f'Request without Authorization header:\nGET {url}\n\nResponse: {response.status_code}',
                    'remediation': 'Implement authentication for all sensitive endpoints. Reject requests without valid credentials.',
                    'cvss_score': 7.5
                })
            else:
                self.logger.info(f"✓ Endpoint correctly requires authentication (status: {response.status_code})")

        except Exception as e:
            self.logger.error(f"Error testing missing authentication: {str(e)}")

        # Test 2: Invalid Token
        self.logger.info("\n[AUTH TEST 2] Testing with invalid authentication")
        try:
            invalid_headers = {'Authorization': 'Bearer invalid_token_12345'}
            response = requests.get(url, headers=invalid_headers, timeout=10)
            self.logger.info(f"Response status with invalid token: {response.status_code}")

            if response.status_code == 200:
                self.logger.warning("⚠️  VULNERABILITY FOUND: Endpoint accepts invalid tokens!")
                self.add_vulnerability({
                    'endpoint': url,
                    'method': 'GET',
                    'vulnerability_type': 'broken_authentication',
                    'severity': 'critical',
                    'title': 'Broken Authentication',
                    'description': 'The endpoint accepts invalid authentication tokens.',
                    'proof_of_concept': f'Request with invalid token:\nGET {url}\nAuthorization: Bearer invalid_token_12345\n\nResponse: {response.status_code}',
                    'remediation': 'Properly validate all authentication tokens. Reject invalid tokens with 401 Unauthorized.',
                    'cvss_score': 9.8
                })
            else:
                self.logger.info(f"✓ Endpoint correctly rejects invalid tokens (status: {response.status_code})")

        except Exception as e:
            self.logger.error(f"Error testing invalid authentication: {str(e)}")

    def test_rate_limiting(self, url: str, auth_headers: Dict) -> None:
        """Test for rate limiting"""
        self.logger.info("\n[RATE LIMIT TESTING] Testing rate limiting")

        num_requests = 20
        success_count = 0

        self.logger.info(f"Sending {num_requests} rapid requests...")

        start_time = time.time()
        for i in range(num_requests):
            try:
                response = requests.get(url, headers=auth_headers, timeout=10)
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    self.logger.info(f"✓ Rate limit triggered at request {i+1}")
                    return

            except Exception as e:
                self.logger.error(f"Error in rate limit test request {i+1}: {str(e)}")

        elapsed_time = time.time() - start_time

        if success_count == num_requests:
            self.logger.warning(f"⚠️  VULNERABILITY FOUND: No rate limiting detected ({num_requests} requests in {elapsed_time:.2f}s)")
            self.add_vulnerability({
                'endpoint': url,
                'method': 'GET',
                'vulnerability_type': 'no_rate_limiting',
                'severity': 'medium',
                'title': 'Missing Rate Limiting',
                'description': f'The endpoint has no rate limiting. Successfully made {num_requests} requests in {elapsed_time:.2f} seconds.',
                'proof_of_concept': f'Sent {num_requests} rapid requests to {url}\nAll requests succeeded (200 OK)\nTime taken: {elapsed_time:.2f}s',
                'remediation': 'Implement rate limiting to prevent abuse and DoS attacks. Use techniques like token bucket or sliding window.',
                'cvss_score': 5.3
            })
        else:
            self.logger.info(f"✓ Some rate limiting appears to be in place ({success_count}/{num_requests} succeeded)")

    def test_mass_assignment(self, url: str, auth_headers: Dict) -> None:
        """Test for mass assignment vulnerabilities"""
        self.logger.info("\n[MASS ASSIGNMENT TESTING] Testing mass assignment")

        # Only test POST/PUT/PATCH endpoints
        if not any(method in url.lower() for method in ['post', 'put', 'patch']):
            # Try POST method
            self.logger.info("Testing with POST method")

            # Test payloads with privileged fields
            test_payloads = [
                {'is_admin': True, 'role': 'admin'},
                {'is_admin': 'true', 'admin': True},
                {'role': 'administrator', 'permissions': 'all'},
                {'user_type': 'admin', 'privilege_level': 10}
            ]

            for payload in test_payloads:
                self.logger.info(f"\n[MASS ASSIGNMENT TEST] Testing payload: {json.dumps(payload)}")

                try:
                    response = requests.post(url, json=payload, headers=auth_headers, timeout=10)
                    self.logger.info(f"Response status: {response.status_code}")

                    if response.status_code in [200, 201]:
                        try:
                            response_data = response.json()
                            self.logger.info(f"Response data: {json.dumps(response_data, indent=2)[:500]}...")

                            # Check if our injected fields appear in response
                            for key in payload.keys():
                                if key in str(response_data).lower():
                                    self.logger.warning(f"⚠️  VULNERABILITY FOUND: Mass assignment possible! Field '{key}' was accepted.")
                                    self.add_vulnerability({
                                        'endpoint': url,
                                        'method': 'POST',
                                        'vulnerability_type': 'mass_assignment',
                                        'severity': 'high',
                                        'title': 'Mass Assignment Vulnerability',
                                        'description': f'The endpoint accepts sensitive fields that should not be user-modifiable. Field "{key}" was accepted in the request.',
                                        'proof_of_concept': f'POST {url}\nPayload: {json.dumps(payload, indent=2)}\n\nResponse ({response.status_code}):\n{json.dumps(response_data, indent=2)[:500]}...',
                                        'remediation': 'Implement allowlist of accepted fields. Reject or ignore sensitive fields like is_admin, role, permissions.',
                                        'cvss_score': 8.0
                                    })
                                    return  # Found one, that's enough
                        except:
                            pass
                    else:
                        self.logger.info(f"Payload rejected (status: {response.status_code})")

                except Exception as e:
                    self.logger.error(f"Error testing mass assignment: {str(e)}")

            self.logger.info("✓ No obvious mass assignment vulnerabilities detected")

    def add_vulnerability(self, vuln: Dict) -> None:
        """Add a vulnerability to the list"""
        self.vulnerabilities.append(vuln)
        self.logger.warning(f"\n{'*'*60}")
        self.logger.warning(f"VULNERABILITY FOUND: {vuln['title']}")
        self.logger.warning(f"Severity: {vuln['severity'].upper()}")
        self.logger.warning(f"Type: {vuln['vulnerability_type']}")
        self.logger.warning(f"{'*'*60}\n")


def setup_logging(test_id: int) -> Tuple[logging.Logger, str]:
    """Setup logging for API security test"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/api_test_{test_id}_{timestamp}.log"

    # Create logs directory if it doesn't exist
    import os
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(f"api_test_{test_id}")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []  # Clear any existing handlers

    # File handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger, log_filename
