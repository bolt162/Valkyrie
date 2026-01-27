"""
Smart Fuzzing & Discovery Engine
Advanced directory/file fuzzing, admin panel discovery, parameter fuzzing
"""

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import logging
from typing import List, Dict, Set
from urllib.parse import urlparse, urljoin, parse_qs, urlunparse
import itertools


class FuzzingEngine:
    def __init__(self, target_url: str, logger: logging.Logger = None):
        """
        Initialize Fuzzing Engine

        Args:
            target_url: Target URL to fuzz
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

        self.discovered_paths: Set[str] = set()
        self.discovered_parameters: Dict[str, List[str]] = {}
        self.vulnerabilities = []

    def run_all_fuzzing(self) -> Dict:
        """Run all fuzzing techniques"""

        self.logger.info("="*80)
        self.logger.info("Starting Smart Fuzzing & Discovery")
        self.logger.info("="*80)

        # 1. Directory/File Fuzzing
        self.fuzz_directories()

        # 2. Admin Panel Discovery
        self.discover_admin_panels()

        # 3. Cloud Storage Discovery
        self.discover_cloud_storage()

        # 4. Parameter Fuzzing
        self.fuzz_parameters()

        # 5. Backup File Discovery
        self.fuzz_backup_files()

        self.logger.info("="*80)
        self.logger.info(f"Fuzzing complete! Found {len(self.discovered_paths)} paths")
        self.logger.info("="*80)

        return {
            'discovered_paths': sorted(list(self.discovered_paths)),
            'discovered_parameters': self.discovered_parameters,
            'vulnerabilities': self.vulnerabilities,
        }

    def fuzz_directories(self) -> None:
        """Fuzz common directories and files"""
        self.logger.info("\n[DIRECTORY FUZZING] Testing common directories...")

        common_dirs = [
            # Admin/Management
            '/admin',
            '/administrator',
            '/adminpanel',
            '/admin-panel',
            '/control-panel',
            '/controlpanel',
            '/management',
            '/manager',
            '/portal',
            '/dashboard',
            '/cpanel',
            '/wp-admin',
            '/phpmyadmin',
            '/pma',
            '/mysql',
            '/db',
            '/database',
            # API/Services
            '/api',
            '/api/v1',
            '/api/v2',
            '/rest',
            '/graphql',
            '/services',
            '/ws',
            '/rpc',
            # Development/Testing
            '/dev',
            '/development',
            '/test',
            '/testing',
            '/stage',
            '/staging',
            '/uat',
            '/qa',
            '/demo',
            '/sandbox',
            '/temp',
            '/tmp',
            # Documentation
            '/docs',
            '/documentation',
            '/doc',
            '/help',
            '/support',
            # Backups
            '/backup',
            '/backups',
            '/old',
            '/archive',
            # Config
            '/config',
            '/configuration',
            '/settings',
            '/setup',
            # Files
            '/upload',
            '/uploads',
            '/files',
            '/downloads',
            '/images',
            '/media',
            '/assets',
            '/static',
            '/public',
            # Logs
            '/logs',
            '/log',
            '/debug',
            '/trace',
            # Git
            '/.git',
            '/.gitignore',
            '/.git/config',
            '/.git/HEAD',
            # Environment
            '/.env',
            '/.env.local',
            '/.env.production',
            # Other sensitive
            '/.ssh',
            '/.aws',
            '/credentials',
            '/secrets',
        ]

        for path in common_dirs:
            try:
                url = urljoin(self.base_url, path)
                response = self.session.get(url, timeout=5, verify=False, allow_redirects=False)

                # Consider 200, 401, 403 as existing paths
                if response.status_code in [200, 201, 301, 302, 401, 403, 405]:
                    self.discovered_paths.add(path)

                    # Log based on status
                    if response.status_code == 200:
                        self.logger.info(f"✓ Found accessible: {path} [200]")

                        # Check if it's a sensitive directory
                        if any(sensitive in path.lower() for sensitive in ['admin', 'backup', '.git', '.env', 'config', 'db']):
                            self.add_vulnerability({
                                'vulnerability_type': 'exposed_sensitive_directory',
                                'severity': 'high' if '.git' in path or '.env' in path else 'medium',
                                'title': f'Exposed Sensitive Directory: {path}',
                                'description': f'Sensitive directory {path} is accessible without authentication',
                                'proof_of_concept': f'GET {url} returns 200 OK',
                                'remediation': 'Restrict access to sensitive directories with authentication or remove them from production',
                                'endpoint': path,
                                'method': 'GET'
                            })

                    elif response.status_code in [401, 403]:
                        self.logger.info(f"✓ Found protected: {path} [{response.status_code}]")

            except Exception as e:
                self.logger.debug(f"Path {path} not found: {str(e)}")

    def discover_admin_panels(self) -> None:
        """Discover admin panels and login pages"""
        self.logger.info("\n[ADMIN PANEL DISCOVERY] Searching for admin panels...")

        admin_paths = [
            # Generic admin
            '/admin',
            '/admin/',
            '/admin.php',
            '/admin.html',
            '/admin/login',
            '/admin/login.php',
            '/admin/index.php',
            '/administrator',
            '/administrator/',
            '/administrator/index.php',
            '/admincp',
            '/adminpanel',
            '/admin-panel',
            '/admin_area',
            '/adminarea',
            '/admin_login',
            # CMS-specific
            '/wp-admin',
            '/wp-login.php',
            '/user/login',
            '/user/admin',
            '/admin1',
            '/admin2',
            '/admin3',
            '/admin4',
            '/admin5',
            '/moderator',
            '/webadmin',
            '/adminarea',
            '/bb-admin',
            '/cmsadmin',
            '/admin_home',
            '/adm',
            '/controlpanel',
            '/control',
            '/cp',
            '/admin_panel',
            # Framework-specific
            '/django-admin',
            '/admin/login/',
            '/panel',
            '/backend',
            # Database
            '/phpmyadmin',
            '/pma',
            '/phpMyAdmin',
            '/mysql',
            '/mysqladmin',
            '/sqladmin',
            '/db',
            '/database',
            '/dbadmin',
            '/myadmin',
        ]

        for path in admin_paths:
            try:
                url = urljoin(self.base_url, path)
                response = self.session.get(url, timeout=5, verify=False)

                if response.status_code == 200:
                    content = response.text.lower()

                    # Check if it looks like a login page
                    login_indicators = ['password', 'username', 'login', 'signin', 'log in', 'sign in']
                    is_login = any(indicator in content for indicator in login_indicators)

                    if is_login:
                        self.logger.warning(f"⚠️  Found admin panel: {path}")
                        self.discovered_paths.add(path)

                        self.add_vulnerability({
                            'vulnerability_type': 'exposed_admin_panel',
                            'severity': 'medium',
                            'title': f'Exposed Admin Panel: {path}',
                            'description': f'Admin login panel is publicly accessible at {path}',
                            'proof_of_concept': f'GET {url} returns login form\n\nPage contains: {", ".join([i for i in login_indicators if i in content][:3])}',
                            'remediation': 'Protect admin panels with IP whitelisting, VPN, or additional authentication layer',
                            'endpoint': path,
                            'method': 'GET',
                            'cvss_score': 5.0
                        })

            except Exception as e:
                self.logger.debug(f"Admin path {path} not found: {str(e)}")

    def discover_cloud_storage(self) -> None:
        """Discover cloud storage buckets"""
        self.logger.info("\n[CLOUD STORAGE] Checking for exposed cloud storage...")

        # Extract domain components for bucket naming
        domain_parts = self.domain.replace('.', '-').split('-')
        company_names = [part for part in domain_parts if part not in ['com', 'net', 'org', 'io', 'co', 'www']]

        bucket_patterns = []
        for name in company_names[:2]:  # Limit to first 2 parts
            bucket_patterns.extend([
                name,
                f'{name}-backup',
                f'{name}-backups',
                f'{name}-dev',
                f'{name}-prod',
                f'{name}-production',
                f'{name}-staging',
                f'{name}-assets',
                f'{name}-uploads',
                f'{name}-media',
                f'{name}-files',
                f'{name}-data',
            ])

        # Check S3 buckets
        for bucket in bucket_patterns:
            s3_url = f'https://{bucket}.s3.amazonaws.com'
            try:
                response = self.session.get(s3_url, timeout=3, verify=False)

                if response.status_code in [200, 403]:
                    self.logger.warning(f"⚠️  Found S3 bucket: {bucket}")
                    self.discovered_paths.add(s3_url)

                    if response.status_code == 200:
                        self.add_vulnerability({
                            'vulnerability_type': 'exposed_s3_bucket',
                            'severity': 'critical',
                            'title': f'Publicly Accessible S3 Bucket: {bucket}',
                            'description': f'S3 bucket {bucket} is publicly accessible and may contain sensitive data',
                            'proof_of_concept': f'GET {s3_url} returns 200 OK\n\nBucket contents may be listable',
                            'remediation': 'Review S3 bucket permissions and restrict public access',
                            'endpoint': s3_url,
                            'method': 'GET',
                            'cvss_score': 9.0
                        })
                    else:
                        self.logger.info(f"  Bucket exists but is protected: {bucket}")

            except Exception as e:
                self.logger.debug(f"S3 bucket {bucket} not found: {str(e)}")

    def fuzz_parameters(self) -> None:
        """Fuzz common API parameters"""
        self.logger.info("\n[PARAMETER FUZZING] Testing common parameters...")

        common_params = [
            # IDs and identifiers
            'id',
            'user_id',
            'userId',
            'uid',
            'account_id',
            'accountId',
            'customer_id',
            'customerId',
            # Boolean flags
            'admin',
            'is_admin',
            'isAdmin',
            'debug',
            'test',
            'dev',
            # Data retrieval
            'limit',
            'offset',
            'page',
            'per_page',
            'perPage',
            'sort',
            'order',
            'filter',
            # File operations
            'file',
            'filename',
            'path',
            'url',
            'redirect',
            'callback',
            # Other
            'format',
            'type',
            'action',
            'method',
        ]

        # Test on base URL
        self.logger.info(f"Testing parameters on {self.base_url}")

        for param in common_params[:10]:  # Test first 10 to avoid too many requests
            try:
                # Test with different values
                test_values = ['1', 'true', 'test']

                for value in test_values:
                    url = f"{self.base_url}?{param}={value}"
                    response = self.session.get(url, timeout=3, verify=False)

                    # Check if parameter is reflected or causes different response
                    if value in response.text or response.status_code != 404:
                        if param not in self.discovered_parameters:
                            self.discovered_parameters[param] = []

                        self.logger.info(f"✓ Parameter accepted: {param}")
                        break

            except Exception as e:
                self.logger.debug(f"Parameter {param} test failed: {str(e)}")

    def fuzz_backup_files(self) -> None:
        """Fuzz for backup files"""
        self.logger.info("\n[BACKUP FILES] Searching for backup files...")

        # Common filenames
        filenames = ['index', 'config', 'app', 'main', 'database', 'db', 'backup', 'admin']

        # Backup extensions
        backup_extensions = [
            '.bak',
            '.old',
            '.backup',
            '.swp',
            '.swo',
            '.tmp',
            '.save',
            '.orig',
            '~',
            '.copy',
            '.zip',
            '.tar.gz',
            '.sql',
        ]

        test_files = []
        for filename in filenames[:5]:  # Limit to avoid too many requests
            for ext in backup_extensions[:5]:
                test_files.append(f'/{filename}{ext}')

        for file_path in test_files:
            try:
                url = urljoin(self.base_url, file_path)
                response = self.session.get(url, timeout=3, verify=False)

                if response.status_code == 200 and len(response.content) > 0:
                    self.logger.warning(f"⚠️  Found backup file: {file_path}")
                    self.discovered_paths.add(file_path)

                    self.add_vulnerability({
                        'vulnerability_type': 'exposed_backup_file',
                        'severity': 'high',
                        'title': f'Exposed Backup File: {file_path}',
                        'description': f'Backup file {file_path} is publicly accessible',
                        'proof_of_concept': f'GET {url} returns 200 OK\nFile size: {len(response.content)} bytes',
                        'remediation': 'Remove backup files from production servers',
                        'endpoint': file_path,
                        'method': 'GET',
                        'cvss_score': 7.5
                    })

            except Exception as e:
                self.logger.debug(f"Backup file {file_path} not found: {str(e)}")

    def add_vulnerability(self, vuln: Dict) -> None:
        """Add a vulnerability to the list"""
        self.vulnerabilities.append(vuln)
        self.logger.warning(f"\n{'*'*60}")
        self.logger.warning(f"VULNERABILITY: {vuln['title']}")
        self.logger.warning(f"Severity: {vuln['severity'].upper()}")
        self.logger.warning(f"{'*'*60}\n")
