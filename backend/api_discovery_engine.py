"""
API Discovery & Enumeration Engine
Automatically discovers API endpoints, subdomains, and technologies from a target URL
"""

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import re
import json
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse, urljoin
import logging
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


class ApiDiscoveryEngine:
    def __init__(self, target_url: str, logger: logging.Logger = None):
        """
        Initialize API Discovery Engine

        Args:
            target_url: Target URL to discover APIs from
            logger: Logger instance
        """
        self.target_url = target_url.rstrip('/')
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Valkyrie-Security-Scanner/1.0'})

        # Parse base domain
        parsed = urlparse(target_url)
        self.domain = parsed.netloc
        self.scheme = parsed.scheme or 'https'
        self.base_url = f"{self.scheme}://{self.domain}"

        # Discovery results
        self.discovered_endpoints: Set[str] = set()
        self.discovered_subdomains: Set[str] = set()
        self.technologies: Dict[str, str] = {}
        self.api_documentation: List[str] = []

    def discover_all(self) -> Dict:
        """
        Run all discovery techniques

        Returns:
            Dictionary with all discoveries
        """
        self.logger.info("="*80)
        self.logger.info(f"Starting API Discovery for: {self.target_url}")
        self.logger.info("="*80)

        # 1. Parse robots.txt
        self.discover_from_robots()

        # 2. Parse sitemap.xml
        self.discover_from_sitemap()

        # 3. Common API path fuzzing
        self.fuzz_common_api_paths()

        # 4. API documentation discovery
        self.discover_api_docs()

        # 5. Crawl JavaScript for API endpoints
        self.discover_from_javascript()

        # 6. Technology detection
        self.detect_technologies()

        # 7. Subdomain enumeration (basic)
        self.enumerate_subdomains()

        self.logger.info("="*80)
        self.logger.info(f"Discovery Complete!")
        self.logger.info(f"Found {len(self.discovered_endpoints)} endpoints")
        self.logger.info(f"Found {len(self.discovered_subdomains)} subdomains")
        self.logger.info(f"Detected {len(self.technologies)} technologies")
        self.logger.info("="*80)

        return {
            'endpoints': sorted(list(self.discovered_endpoints)),
            'subdomains': sorted(list(self.discovered_subdomains)),
            'technologies': self.technologies,
            'api_documentation': self.api_documentation,
        }

    def discover_from_robots(self) -> None:
        """Discover endpoints from robots.txt"""
        self.logger.info("\n[ROBOTS.TXT] Checking robots.txt...")

        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            response = self.session.get(robots_url, timeout=10, verify=False)

            if response.status_code == 200:
                self.logger.info(f"✓ Found robots.txt")

                # Parse robots.txt for Disallow and Allow paths
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.startswith('Disallow:') or line.startswith('Allow:'):
                        path = line.split(':', 1)[1].strip()
                        if path and path != '/' and not path.startswith('*'):
                            # Clean and add endpoint
                            clean_path = path.split('?')[0].split('#')[0]
                            if clean_path:
                                self.discovered_endpoints.add(clean_path)
                                self.logger.info(f"  Found: {clean_path}")
            else:
                self.logger.info(f"✗ No robots.txt found")

        except Exception as e:
            self.logger.error(f"Error checking robots.txt: {str(e)}")

    def discover_from_sitemap(self) -> None:
        """Discover endpoints from sitemap.xml"""
        self.logger.info("\n[SITEMAP.XML] Checking sitemap.xml...")

        sitemap_urls = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap-index.xml',
            '/sitemap1.xml',
        ]

        for sitemap_path in sitemap_urls:
            try:
                sitemap_url = urljoin(self.base_url, sitemap_path)
                response = self.session.get(sitemap_url, timeout=10, verify=False)

                if response.status_code == 200:
                    self.logger.info(f"✓ Found {sitemap_path}")

                    # Parse XML
                    try:
                        root = ET.fromstring(response.content)

                        # Handle namespaces
                        namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

                        # Extract URLs
                        for url_elem in root.findall('.//sm:loc', namespaces):
                            url = url_elem.text
                            if url:
                                parsed = urlparse(url)
                                path = parsed.path
                                if path and path != '/':
                                    self.discovered_endpoints.add(path)
                                    if 'api' in path.lower():
                                        self.logger.info(f"  Found API endpoint: {path}")

                        # Also check for non-namespaced URLs
                        for url_elem in root.findall('.//loc'):
                            url = url_elem.text
                            if url:
                                parsed = urlparse(url)
                                path = parsed.path
                                if path and path != '/' and 'api' in path.lower():
                                    self.discovered_endpoints.add(path)
                                    self.logger.info(f"  Found API endpoint: {path}")

                    except ET.ParseError:
                        self.logger.error(f"Failed to parse {sitemap_path}")

                    break  # Found a sitemap, no need to check others

            except Exception as e:
                self.logger.debug(f"Error checking {sitemap_path}: {str(e)}")

    def fuzz_common_api_paths(self) -> None:
        """Fuzz common API paths"""
        self.logger.info("\n[API PATH FUZZING] Testing common API paths...")

        common_paths = [
            # API versioning
            '/api',
            '/api/v1',
            '/api/v2',
            '/api/v3',
            '/v1',
            '/v2',
            '/v3',
            # REST conventions
            '/rest',
            '/rest/v1',
            '/restapi',
            # GraphQL
            '/graphql',
            '/graphiql',
            '/gql',
            # Common endpoints
            '/api/users',
            '/api/auth',
            '/api/login',
            '/api/data',
            '/api/products',
            '/api/items',
            # Alternative naming
            '/services',
            '/webservice',
            '/ws',
            '/service',
            # OWASP Juice Shop / Node.js REST API patterns
            '/rest/user/login',
            '/rest/user/whoami',
            '/rest/user/change-password',
            '/rest/products/search',
            '/rest/saveLoginIp',
            '/rest/basket',
            '/rest/wallet/balance',
            '/api/Users',
            '/api/Products',
            '/api/Feedbacks',
            '/api/Challenges',
            '/api/Complaints',
            '/api/Recycles',
            '/api/SecurityQuestions',
            '/api/SecurityAnswers',
            '/api/Cards',
            '/api/Addresss',
            '/api/Quantitys',
        ]

        for path in common_paths:
            try:
                url = urljoin(self.base_url, path)
                response = self.session.get(url, timeout=5, verify=False, allow_redirects=False)

                # Consider 200, 401, 403 as existing endpoints
                if response.status_code in [200, 201, 401, 403, 405]:
                    self.discovered_endpoints.add(path)
                    self.logger.info(f"✓ Found: {path} [{response.status_code}]")

                    # Check if it's GraphQL
                    if 'graphql' in path.lower():
                        self.technologies['graphql'] = 'detected'

            except Exception as e:
                self.logger.debug(f"Error testing {path}: {str(e)}")

    def discover_api_docs(self) -> None:
        """Discover API documentation endpoints"""
        self.logger.info("\n[API DOCUMENTATION] Checking for API docs...")

        doc_paths = [
            # Swagger/OpenAPI
            '/swagger',
            '/swagger-ui',
            '/swagger-ui.html',
            '/swagger/index.html',
            '/api-docs',
            '/api/docs',
            '/api/swagger',
            '/api/swagger.json',
            '/api/swagger.yaml',
            '/swagger.json',
            '/swagger.yaml',
            '/openapi.json',
            '/openapi.yaml',
            '/v1/swagger.json',
            '/v2/swagger.json',
            '/v3/swagger.json',
            # ReDoc
            '/redoc',
            '/api/redoc',
            # Other documentation
            '/docs',
            '/documentation',
            '/api/documentation',
            '/api-doc',
            '/api/reference',
            # GraphQL
            '/graphiql',
            '/graphql/playground',
            '/playground',
        ]

        for path in doc_paths:
            try:
                url = urljoin(self.base_url, path)
                response = self.session.get(url, timeout=5, verify=False)

                if response.status_code == 200:
                    self.api_documentation.append(path)
                    self.discovered_endpoints.add(path)
                    self.logger.info(f"✓ Found API docs: {path}")

                    # Parse Swagger/OpenAPI JSON
                    if 'json' in path.lower():
                        try:
                            swagger_data = response.json()
                            if 'paths' in swagger_data:
                                self.logger.info(f"  Parsing OpenAPI spec...")
                                for endpoint_path in swagger_data['paths'].keys():
                                    self.discovered_endpoints.add(endpoint_path)
                                    self.logger.info(f"    Found: {endpoint_path}")
                        except:
                            pass

            except Exception as e:
                self.logger.debug(f"Error checking {path}: {str(e)}")

    def discover_from_javascript(self) -> None:
        """Extract API endpoints from JavaScript files"""
        self.logger.info("\n[JAVASCRIPT ANALYSIS] Analyzing JavaScript for API calls...")

        try:
            # Get main page
            response = self.session.get(self.base_url, timeout=10, verify=False)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all script tags
                scripts = soup.find_all('script', src=True)

                self.logger.info(f"Found {len(scripts)} external JavaScript files")

                # Limit to first 10 scripts to avoid too many requests
                for script in scripts[:10]:
                    src = script.get('src')
                    if src:
                        script_url = urljoin(self.base_url, src)

                        try:
                            js_response = self.session.get(script_url, timeout=5, verify=False)
                            if js_response.status_code == 200:
                                # Extract API endpoints using regex
                                js_content = js_response.text

                                # Look for common patterns
                                patterns = [
                                    r'["\']/(api/[a-zA-Z0-9/_-]+)["\']',
                                    r'["\']/(v\d+/[a-zA-Z0-9/_-]+)["\']',
                                    r'["\']/(graphql)["\']',
                                    r'fetch\(["\']([/a-zA-Z0-9/_-]+)["\']',
                                    r'axios\.(get|post|put|delete)\(["\']([/a-zA-Z0-9/_-]+)["\']',
                                ]

                                for pattern in patterns:
                                    matches = re.findall(pattern, js_content, re.IGNORECASE)
                                    for match in matches:
                                        # Handle tuple results from regex groups
                                        endpoint = match if isinstance(match, str) else match[-1]
                                        if endpoint and endpoint.startswith('/'):
                                            self.discovered_endpoints.add(endpoint)
                                            if len(self.discovered_endpoints) % 10 == 0:
                                                self.logger.info(f"  Found {len(self.discovered_endpoints)} endpoints so far...")

                        except Exception as e:
                            self.logger.debug(f"Error analyzing script {src}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error analyzing JavaScript: {str(e)}")

    def detect_technologies(self) -> None:
        """Detect technologies and frameworks"""
        self.logger.info("\n[TECHNOLOGY DETECTION] Detecting technologies...")

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)

            # Check headers
            headers = response.headers

            # Server detection
            if 'Server' in headers:
                self.technologies['server'] = headers['Server']
                self.logger.info(f"✓ Server: {headers['Server']}")

            # Framework detection from headers
            framework_headers = {
                'X-Powered-By': 'framework',
                'X-AspNet-Version': 'aspnet_version',
                'X-AspNetMvc-Version': 'aspnet_mvc_version',
            }

            for header, tech_name in framework_headers.items():
                if header in headers:
                    self.technologies[tech_name] = headers[header]
                    self.logger.info(f"✓ {tech_name}: {headers[header]}")

            # Content-based detection
            content = response.text.lower()

            # Framework detection
            frameworks = {
                'react': ['react', '_reactroot'],
                'vue': ['vue.js', 'vue.min.js', '__vue__'],
                'angular': ['ng-', 'angular.js', 'angular.min.js'],
                'django': ['csrfmiddlewaretoken', 'django'],
                'express': ['express', 'x-powered-by: express'],
                'flask': ['flask'],
                'laravel': ['laravel', 'csrf-token'],
                'wordpress': ['wp-content', 'wp-includes'],
            }

            for framework, indicators in frameworks.items():
                if any(indicator in content for indicator in indicators):
                    self.technologies[framework] = 'detected'
                    self.logger.info(f"✓ Framework: {framework}")

            # Check for GraphQL
            if any(path for path in self.discovered_endpoints if 'graphql' in path.lower()):
                self.technologies['graphql'] = 'detected'
                self.logger.info(f"✓ API Type: GraphQL")

        except Exception as e:
            self.logger.error(f"Error detecting technologies: {str(e)}")

    def enumerate_subdomains(self) -> None:
        """Basic subdomain enumeration"""
        self.logger.info("\n[SUBDOMAIN ENUMERATION] Checking common subdomains...")

        # Extract root domain (handle subdomains)
        domain_parts = self.domain.split('.')
        if len(domain_parts) >= 2:
            root_domain = '.'.join(domain_parts[-2:])
        else:
            root_domain = self.domain

        common_subdomains = [
            'api',
            'dev',
            'staging',
            'test',
            'uat',
            'admin',
            'portal',
            'app',
            'www',
            'api-dev',
            'api-staging',
            'api-test',
            'dev-api',
            'staging-api',
            'rest',
            'graphql',
            'v1',
            'v2',
        ]

        for subdomain in common_subdomains:
            full_domain = f"{subdomain}.{root_domain}"

            try:
                # Try to resolve and connect
                test_url = f"{self.scheme}://{full_domain}"
                response = self.session.get(test_url, timeout=3, verify=False, allow_redirects=False)

                # If we get any response, subdomain exists
                if response.status_code < 500:
                    self.discovered_subdomains.add(full_domain)
                    self.logger.info(f"✓ Found subdomain: {full_domain} [{response.status_code}]")

            except Exception as e:
                self.logger.debug(f"Subdomain {full_domain} not found: {str(e)}")


def setup_discovery_logging(test_id: int) -> tuple:
    """Setup logging for API discovery"""
    from datetime import datetime
    import os

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/api_discovery_{test_id}_{timestamp}.log"

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(f"api_discovery_{test_id}")
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
