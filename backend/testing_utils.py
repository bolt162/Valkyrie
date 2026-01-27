"""
Testing Utilities
Helper functions for intelligent security testing
"""

import re
from typing import List
from urllib.parse import urlparse


def is_public_endpoint(endpoint: str) -> bool:
    """
    Check if an endpoint is meant to be public (should skip authentication tests)

    Args:
        endpoint: The endpoint path to check

    Returns:
        True if endpoint is meant to be public
    """
    endpoint_lower = endpoint.lower()

    # Known public endpoints
    public_patterns = [
        # SEO files
        r'/robots\.txt$',
        r'/sitemap.*\.xml$',
        r'.*-sitemap\.xml$',
        r'/sitemap\.xml$',
        r'/sitemap_index\.xml$',

        # Favicons and app icons
        r'/favicon\.ico$',
        r'/apple-touch-icon.*\.png$',
        r'/android-chrome.*\.png$',
        r'/site\.webmanifest$',

        # Common public files
        r'/manifest\.json$',
        r'/browserconfig\.xml$',
        r'/.well-known/.*',

        # Static assets (common patterns)
        r'/static/.*',
        r'/assets/.*',
        r'/public/.*',
        r'/images/.*',
        r'/img/.*',
        r'/css/.*',
        r'/js/.*',
        r'/fonts/.*',

        # Security and policy files
        r'/security\.txt$',
        r'/.well-known/security\.txt$',
        r'/privacy.*\.html?$',
        r'/terms.*\.html?$',

        # Health/Status endpoints (often public for monitoring)
        r'/health$',
        r'/healthcheck$',
        r'/status$',
        r'/ping$',
    ]

    for pattern in public_patterns:
        if re.search(pattern, endpoint_lower):
            return True

    return False


def is_readonly_resource(endpoint: str) -> bool:
    """
    Check if an endpoint represents a read-only resource
    (should skip PUT/DELETE/POST tests)

    Args:
        endpoint: The endpoint path to check

    Returns:
        True if endpoint is read-only
    """
    endpoint_lower = endpoint.lower()

    # Read-only file extensions
    readonly_extensions = [
        '.xml',
        '.txt',
        '.html',
        '.htm',
        '.pdf',
        '.jpg',
        '.jpeg',
        '.png',
        '.gif',
        '.svg',
        '.ico',
        '.css',
        '.js',
        '.woff',
        '.woff2',
        '.ttf',
        '.eot',
        '.json',  # Usually read-only config files
        '.md',
        '.webmanifest',
    ]

    for ext in readonly_extensions:
        if endpoint_lower.endswith(ext):
            return True

    # Check for sitemap patterns even without .xml extension
    if 'sitemap' in endpoint_lower or 'robots' in endpoint_lower:
        return True

    return False


def should_skip_auth_test(endpoint: str, test_type: str) -> bool:
    """
    Determine if authentication test should be skipped for this endpoint

    Args:
        endpoint: The endpoint path
        test_type: Type of test (e.g., 'auth', 'bola', 'jwt')

    Returns:
        True if test should be skipped
    """
    # Skip auth tests on public endpoints
    if is_public_endpoint(endpoint):
        return True

    return False


def should_skip_write_methods(endpoint: str) -> bool:
    """
    Determine if write methods (PUT/POST/DELETE) should be skipped

    Args:
        endpoint: The endpoint path

    Returns:
        True if write methods should be skipped
    """
    # Skip write methods on read-only resources
    if is_readonly_resource(endpoint):
        return True

    # Skip write methods on public endpoints (usually read-only)
    if is_public_endpoint(endpoint):
        return True

    return False


def get_allowed_methods(endpoint: str) -> List[str]:
    """
    Get list of HTTP methods that should be tested for this endpoint

    Args:
        endpoint: The endpoint path

    Returns:
        List of HTTP methods to test
    """
    # For read-only resources, only test GET
    if is_readonly_resource(endpoint) or is_public_endpoint(endpoint):
        return ['GET']

    # For API endpoints, test all methods
    endpoint_lower = endpoint.lower()
    if any(pattern in endpoint_lower for pattern in ['/api/', '/v1/', '/v2/', '/rest/', '/graphql']):
        return ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

    # Default: test read and write
    return ['GET', 'POST', 'PUT', 'DELETE']


def is_likely_api_endpoint(endpoint: str) -> bool:
    """
    Check if endpoint is likely an API endpoint (vs static file)

    Args:
        endpoint: The endpoint path

    Returns:
        True if endpoint is likely an API
    """
    endpoint_lower = endpoint.lower()

    # API indicators
    api_patterns = [
        '/api/',
        '/v1/',
        '/v2/',
        '/v3/',
        '/rest/',
        '/graphql',
        '/ws/',
        '/rpc/',
    ]

    for pattern in api_patterns:
        if pattern in endpoint_lower:
            return True

    # If it has a file extension, it's probably not an API
    if is_readonly_resource(endpoint):
        return False

    # If it doesn't have an extension and not in static paths, likely an API
    has_extension = '.' in endpoint.split('/')[-1]
    in_static = any(path in endpoint_lower for path in ['/static/', '/assets/', '/public/'])

    return not has_extension and not in_static


def get_endpoint_classification(endpoint: str) -> dict:
    """
    Get comprehensive classification of an endpoint

    Args:
        endpoint: The endpoint path

    Returns:
        Dictionary with classification info
    """
    return {
        'endpoint': endpoint,
        'is_public': is_public_endpoint(endpoint),
        'is_readonly': is_readonly_resource(endpoint),
        'is_api': is_likely_api_endpoint(endpoint),
        'allowed_methods': get_allowed_methods(endpoint),
        'skip_auth_tests': should_skip_auth_test(endpoint, 'auth'),
        'skip_write_methods': should_skip_write_methods(endpoint),
    }
