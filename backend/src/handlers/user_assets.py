"""
User Assets API Handler

Handles requests for getting user asset URLs (photos, etc.)
"""

import json
from utils.response import success_response, error_response, get_user_sub
from utils.s3 import generate_presigned_get_url


def handler(event, context):
    """Handler for GET /user-assets endpoint."""
    try:
        # Handle CORS preflight request
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Max-Age': '86400',
                },
                'body': ''
            }
        
        user_sub = get_user_sub(event)
        if not user_sub:
            return error_response('Unauthorized', 401)

        # Get asset key from query parameters
        query_params = event.get('queryStringParameters') or {}
        asset_key = query_params.get('key')
        
        if not asset_key:
            return error_response('asset key parameter required', 400)

        # Generate presigned GET URL for the asset
        url = generate_presigned_get_url(asset_key, expiration=3600)  # 1 hour expiration
        
        return success_response({
            'url': url,
            'key': asset_key
        })

    except Exception as e:
        print(f'Error getting user asset: {e}')
        return error_response('Failed to get user asset', 500)
