import json
from typing import Any, Dict, Optional

CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Max-Age': '86400',
}


def success_response(data: Any, status_code: int = 200) -> Dict:
    """Return a successful API response."""
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(data),
    }


def error_response(message: str, status_code: int = 400) -> Dict:
    """Return an error API response."""
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps({'error': message}),
    }


def get_user_sub(event: Dict) -> Optional[str]:
    """Extract user identifier from API Gateway/Cognito authorizer claims.

    Supports both REST API (claims under requestContext.authorizer.claims)
    and HTTP API (claims under requestContext.authorizer.jwt.claims), and
    falls back to common Cognito keys.
    """
    try:
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        # REST API
        claims: Dict[str, Any] = authorizer.get('claims') or {}
        # HTTP API (JWT authorizer)
        if not claims:
            claims = authorizer.get('jwt', {}).get('claims', {}) or {}

        # Prefer standard Cognito subject; fall back to username keys
        return (
            claims.get('sub')
            or claims.get('username')
            or claims.get('cognito:username')
        )
    except Exception:
        return None
