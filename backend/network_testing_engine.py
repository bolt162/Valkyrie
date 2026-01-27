"""
Network-Level Testing Engine
Port scanning, service detection, WAF/CDN identification
"""

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import socket
import requests
import logging
from typing import List, Dict, Set
from urllib.parse import urlparse
import time
import ssl
import re


class NetworkTestingEngine:
    def __init__(self, target_url: str, logger: logging.Logger = None):
        """
        Initialize Network Testing Engine

        Args:
            target_url: Target URL to test
            logger: Logger instance
        """
        self.target_url = target_url.rstrip('/')
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Valkyrie-Network-Scanner/1.0'})

        parsed = urlparse(target_url)
        self.domain = parsed.netloc
        self.scheme = parsed.scheme or 'https'
        self.base_url = f"{self.scheme}://{self.domain}"

        # Extract hostname (without port if present)
        if ':' in self.domain:
            self.hostname = self.domain.split(':')[0]
        else:
            self.hostname = self.domain

        self.vulnerabilities = []
        self.open_ports = []
        self.service_info = {}

    def run_all_network_tests(self) -> Dict:
        """Run all network-level tests"""

        self.logger.info("="*80)
        self.logger.info("Starting Network-Level Testing")
        self.logger.info("="*80)

        # 1. Port Scanning (Common API/Web Ports)
        self.scan_common_ports()

        # 2. Service Version Detection
        self.detect_services()

        # 3. WAF/CDN Detection
        self.detect_waf_cdn()

        # 4. SSL/TLS Analysis
        self.analyze_ssl_tls()

        # 5. DNS Information
        self.gather_dns_info()

        self.logger.info("="*80)
        self.logger.info(f"Network testing complete! Found {len(self.vulnerabilities)} vulnerabilities")
        self.logger.info(f"Open ports: {len(self.open_ports)}")
        self.logger.info("="*80)

        return {
            'vulnerabilities': self.vulnerabilities,
            'open_ports': self.open_ports,
            'service_info': self.service_info,
        }

    def scan_common_ports(self) -> None:
        """
        Scan common API and web service ports
        Lightweight scan focused on API-relevant ports only
        """
        self.logger.info("\n[PORT SCANNING] Scanning common API/web ports...")

        # Common ports for APIs and web services
        common_ports = {
            80: 'HTTP',
            443: 'HTTPS',
            8080: 'HTTP-Alt',
            8443: 'HTTPS-Alt',
            3000: 'Node.js/React Dev',
            3001: 'React/Dev Server',
            4000: 'GraphQL',
            5000: 'Flask/Python Dev',
            8000: 'Django/Python',
            8001: 'API Server',
            8888: 'HTTP Alt/Jupyter',
            9000: 'API/Service',
            9090: 'Prometheus/API',
        }

        for port, service in common_ports.items():
            if self._check_port(self.hostname, port):
                self.open_ports.append({'port': port, 'service': service})
                self.logger.info(f"✓ Port {port} ({service}) is OPEN")

                # Check if unencrypted services are exposed
                if port in [80, 8080, 3000, 5000, 8000] and self.scheme == 'https':
                    self.add_vulnerability({
                        'vulnerability_type': 'unencrypted_service',
                        'severity': 'medium',
                        'title': f'Unencrypted Service on Port {port}',
                        'description': f'Unencrypted {service} service is accessible on port {port}. This may allow traffic interception.',
                        'proof_of_concept': f'Port {port} ({service}) is open and accessible',
                        'remediation': 'Redirect HTTP traffic to HTTPS or disable HTTP access',
                        'endpoint': f'{self.hostname}:{port}',
                        'method': 'TCP',
                        'cvss_score': 5.0
                    })

        if not self.open_ports:
            self.logger.info("No common API ports found open (this is normal for production services)")

    def _check_port(self, host: str, port: int, timeout: float = 2.0) -> bool:
        """Check if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            self.logger.debug(f"Port check failed for {host}:{port}: {str(e)}")
            return False

    def detect_services(self) -> None:
        """Detect service versions and fingerprints"""
        self.logger.info("\n[SERVICE DETECTION] Detecting services and versions...")

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)

            # Check Server header
            if 'Server' in response.headers:
                server = response.headers['Server']
                self.service_info['server'] = server
                self.logger.info(f"Server: {server}")

                # Check for outdated/vulnerable servers
                outdated_markers = {
                    'apache/2.2': 'Apache 2.2 (EOL since 2017)',
                    'apache/2.0': 'Apache 2.0 (EOL)',
                    'nginx/1.10': 'Nginx 1.10 (outdated)',
                    'nginx/1.8': 'Nginx 1.8 (outdated)',
                    'iis/6': 'IIS 6 (Windows Server 2003, EOL)',
                    'iis/7': 'IIS 7 (Windows Server 2008, EOL)',
                }

                for marker, version_info in outdated_markers.items():
                    if marker in server.lower():
                        self.logger.warning(f"⚠️  Outdated server version detected: {version_info}")
                        self.add_vulnerability({
                            'vulnerability_type': 'outdated_server',
                            'severity': 'high',
                            'title': f'Outdated Server Version: {server}',
                            'description': f'Server is running an outdated version: {version_info}. This may contain known vulnerabilities.',
                            'proof_of_concept': f'Server header: {server}',
                            'remediation': 'Upgrade to the latest stable server version',
                            'endpoint': self.base_url,
                            'method': 'GET',
                            'cvss_score': 7.0
                        })
                        break

            # Check for framework signatures
            framework_headers = {
                'X-Powered-By': 'framework',
                'X-AspNet-Version': 'aspnet_version',
                'X-AspNetMvc-Version': 'aspnetmvc_version',
                'X-Framework': 'framework_name',
            }

            for header, key in framework_headers.items():
                if header in response.headers:
                    self.service_info[key] = response.headers[header]
                    self.logger.info(f"{header}: {response.headers[header]}")

            # Detect technologies from response
            self._detect_technologies_from_response(response)

        except Exception as e:
            self.logger.error(f"Service detection failed: {str(e)}")

    def _detect_technologies_from_response(self, response: requests.Response) -> None:
        """Detect technologies from response content"""
        content = response.text.lower()

        technologies = {
            'wordpress': ['wp-content', 'wp-includes', 'wordpress'],
            'drupal': ['drupal', '/sites/default/'],
            'joomla': ['joomla', 'option=com_'],
            'django': ['csrfmiddlewaretoken', 'django'],
            'flask': ['werkzeug'],
            'express': ['express', 'x-powered-by: express'],
            'laravel': ['laravel', 'laravel_session'],
            'react': ['react', '__react'],
            'vue': ['vue.js', 'vue'],
            'angular': ['ng-', 'angular'],
        }

        detected = []
        for tech, markers in technologies.items():
            if any(marker in content for marker in markers):
                detected.append(tech)
                self.logger.info(f"Detected technology: {tech}")

        if detected:
            self.service_info['detected_technologies'] = detected

    def detect_waf_cdn(self) -> None:
        """Detect WAF and CDN presence"""
        self.logger.info("\n[WAF/CDN DETECTION] Detecting WAF and CDN...")

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)

            # Check for CDN headers
            cdn_headers = {
                'cf-ray': 'Cloudflare',
                'x-amz-cf-id': 'Amazon CloudFront',
                'x-cdn': 'Generic CDN',
                'x-cache': 'Caching Layer',
                'x-served-by': 'Fastly',
                'server': {
                    'cloudflare': 'Cloudflare',
                    'akamaighost': 'Akamai',
                },
            }

            detected_cdn = None

            for header, cdn_name in cdn_headers.items():
                if isinstance(cdn_name, dict):
                    # Check Server header for specific values
                    server_header = response.headers.get('Server', '').lower()
                    for marker, name in cdn_name.items():
                        if marker in server_header:
                            detected_cdn = name
                            break
                elif header.lower() in [h.lower() for h in response.headers]:
                    detected_cdn = cdn_name
                    break

            if detected_cdn:
                self.service_info['cdn'] = detected_cdn
                self.logger.info(f"✓ CDN detected: {detected_cdn}")

            # Test for WAF by sending malicious payloads
            waf_detected = self._test_for_waf()

            if waf_detected:
                self.service_info['waf'] = waf_detected
                self.logger.info(f"✓ WAF detected: {waf_detected}")
            else:
                self.logger.warning("⚠️  No WAF detected - application may be unprotected")
                self.add_vulnerability({
                    'vulnerability_type': 'missing_waf',
                    'severity': 'low',
                    'title': 'No Web Application Firewall Detected',
                    'description': 'No WAF detected protecting the application. Consider implementing a WAF for additional security.',
                    'proof_of_concept': 'No WAF signatures detected in responses',
                    'remediation': 'Implement a WAF like Cloudflare, AWS WAF, or ModSecurity',
                    'endpoint': self.base_url,
                    'method': 'GET',
                    'cvss_score': 3.0
                })

        except Exception as e:
            self.logger.error(f"WAF/CDN detection failed: {str(e)}")

    def _test_for_waf(self) -> str:
        """Test for WAF by sending attack payloads"""
        test_payloads = [
            "' OR '1'='1",
            "<script>alert(1)</script>",
            "../../etc/passwd",
            "UNION SELECT",
        ]

        waf_signatures = {
            'cloudflare': ['cloudflare', 'cf-ray', 'attention required'],
            'akamai': ['akamai', 'reference #'],
            'aws_waf': ['aws', 'request blocked'],
            'imperva': ['imperva', '_incap_'],
            'f5': ['f5', 'bigip'],
            'sucuri': ['sucuri', 'access denied'],
            'wordfence': ['wordfence', 'generated by wordfence'],
        }

        try:
            for payload in test_payloads:
                response = self.session.get(
                    self.base_url,
                    params={'test': payload},
                    timeout=5,
                    verify=False
                )

                # Check if request was blocked (403, 406, etc.)
                if response.status_code in [403, 406, 419, 429, 503]:
                    response_lower = response.text.lower()

                    for waf, signatures in waf_signatures.items():
                        if any(sig in response_lower for sig in signatures):
                            return waf.upper()

                    # Generic WAF detected
                    return "Generic WAF"

        except Exception as e:
            self.logger.debug(f"WAF test failed: {str(e)}")

        return None

    def analyze_ssl_tls(self) -> None:
        """Analyze SSL/TLS configuration"""
        self.logger.info("\n[SSL/TLS ANALYSIS] Analyzing SSL/TLS configuration...")

        if self.scheme != 'https':
            self.logger.warning("⚠️  Target is not using HTTPS")
            self.add_vulnerability({
                'vulnerability_type': 'no_https',
                'severity': 'high',
                'title': 'No HTTPS Encryption',
                'description': 'Target application is not using HTTPS, exposing all traffic to interception',
                'proof_of_concept': f'Target URL uses HTTP: {self.target_url}',
                'remediation': 'Implement HTTPS with a valid SSL/TLS certificate',
                'endpoint': self.base_url,
                'method': 'GET',
                'cvss_score': 7.5
            })
            return

        try:
            # Create SSL context
            context = ssl.create_default_context()

            # Connect and get certificate info
            with socket.create_connection((self.hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    cert = ssock.getpeercert()

                    # Get SSL/TLS version
                    tls_version = ssock.version()
                    self.service_info['tls_version'] = tls_version
                    self.logger.info(f"TLS Version: {tls_version}")

                    # Check for outdated TLS versions
                    if tls_version in ['TLSv1', 'TLSv1.1', 'SSLv2', 'SSLv3']:
                        self.logger.warning(f"⚠️  Outdated TLS version: {tls_version}")
                        self.add_vulnerability({
                            'vulnerability_type': 'outdated_tls',
                            'severity': 'high',
                            'title': f'Outdated TLS Version: {tls_version}',
                            'description': f'Server supports outdated TLS version {tls_version} which has known vulnerabilities',
                            'proof_of_concept': f'TLS version: {tls_version}',
                            'remediation': 'Disable TLS 1.0 and 1.1. Use TLS 1.2 or higher.',
                            'endpoint': self.base_url,
                            'method': 'SSL/TLS',
                            'cvss_score': 7.0
                        })

                    # Get certificate information
                    if cert:
                        subject = dict(x[0] for x in cert['subject'])
                        issuer = dict(x[0] for x in cert['issuer'])

                        self.service_info['ssl_cert'] = {
                            'subject': subject.get('commonName', 'Unknown'),
                            'issuer': issuer.get('organizationName', 'Unknown'),
                        }

                        self.logger.info(f"Certificate Subject: {subject.get('commonName')}")
                        self.logger.info(f"Certificate Issuer: {issuer.get('organizationName')}")

        except ssl.SSLError as e:
            self.logger.warning(f"⚠️  SSL Error: {str(e)}")
            self.add_vulnerability({
                'vulnerability_type': 'ssl_error',
                'severity': 'medium',
                'title': 'SSL/TLS Configuration Error',
                'description': f'SSL/TLS configuration error detected: {str(e)}',
                'proof_of_concept': f'SSL Error: {str(e)}',
                'remediation': 'Review and fix SSL/TLS configuration',
                'endpoint': self.base_url,
                'method': 'SSL/TLS',
                'cvss_score': 5.0
            })
        except Exception as e:
            self.logger.debug(f"SSL/TLS analysis failed: {str(e)}")

    def gather_dns_info(self) -> None:
        """Gather DNS information"""
        self.logger.info("\n[DNS INFORMATION] Gathering DNS information...")

        try:
            # Get IP address
            import socket
            ip_address = socket.gethostbyname(self.hostname)
            self.service_info['ip_address'] = ip_address
            self.logger.info(f"IP Address: {ip_address}")

            # Check if it's a private IP
            if self._is_private_ip(ip_address):
                self.logger.warning(f"⚠️  Target resolves to private IP: {ip_address}")
                self.add_vulnerability({
                    'vulnerability_type': 'private_ip_exposure',
                    'severity': 'low',
                    'title': 'Private IP Address Resolution',
                    'description': f'Target hostname resolves to private IP {ip_address}. This may indicate internal network exposure.',
                    'proof_of_concept': f'{self.hostname} resolves to {ip_address}',
                    'remediation': 'Ensure internal services are not exposed to public DNS',
                    'endpoint': self.hostname,
                    'method': 'DNS',
                    'cvss_score': 4.0
                })

        except Exception as e:
            self.logger.debug(f"DNS lookup failed: {str(e)}")

    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private"""
        try:
            parts = [int(p) for p in ip.split('.')]

            # Check private ranges
            if parts[0] == 10:
                return True
            if parts[0] == 172 and 16 <= parts[1] <= 31:
                return True
            if parts[0] == 192 and parts[1] == 168:
                return True
            if parts[0] == 127:  # Localhost
                return True

            return False
        except:
            return False

    def add_vulnerability(self, vuln: Dict) -> None:
        """Add a vulnerability to the list"""
        self.vulnerabilities.append(vuln)
        self.logger.warning(f"\n{'*'*60}")
        self.logger.warning(f"VULNERABILITY: {vuln['title']}")
        self.logger.warning(f"Severity: {vuln['severity'].upper()}")
        self.logger.warning(f"{'*'*60}\n")
