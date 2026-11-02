"""
Multi-Step Virtual Try-On API Handler

Handles requests for processing multiple clothing items with virtual try-on.
"""

import json
from datetime import datetime
from decimal import Decimal
from utils.response import success_response, error_response, get_user_sub
from services.multi_tryon import process_multi_tryon, get_multi_tryon_status


def convert_decimals(obj):
    """Convert Decimal objects to regular numbers for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    return obj


def handler(event, context):
    """Handler for multi-step virtual try-on requests"""
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
        
        # GET request - check session status
        if event.get('httpMethod') == 'GET':
            session_id = event.get('queryStringParameters', {}).get('session_id')
            if not session_id:
                return error_response('session_id parameter required', 400)
            
            status = get_multi_tryon_status(user_sub, session_id)
            if not status:
                return error_response('Session not found', 404)
            
            # Convert Decimal objects to regular numbers
            status = convert_decimals(status)
            return success_response(status)
        
        # POST request - start multi-step try-on
        if event.get('httpMethod') == 'POST':
            body = json.loads(event.get('body', '{}'))
            
            # Validate required fields
            if not body.get('items') or not isinstance(body.get('items'), list):
                return error_response('items array is required', 400)
            
            if not body.get('body_asset_key'):
                return error_response('body_asset_key is required', 400)
            
            items = body['items']
            body_asset_key = body['body_asset_key']
            session_id = body.get('session_id')  # Optional
            
            # Validate items
            for i, item in enumerate(items):
                if not item.get('imageUrl'):
                    return error_response(f'Item {i+1} missing imageUrl', 400)
                if not item.get('title'):
                    return error_response(f'Item {i+1} missing title', 400)
            
            print(f"🎯 Starting multi-step try-on for {len(items)} items")
            print(f"👤 User: {user_sub}")
            print(f"📸 Body photo: {body_asset_key}")
            
            # Process items
            result = process_multi_tryon(
                user_sub=user_sub,
                items=items,
                body_asset_key=body_asset_key,
                session_id=session_id
            )
            
            return success_response(result)
        
        return error_response('Method not allowed', 405)
        
    except Exception as e:
        print(f'Error in multi-fit handler: {e}')
        import traceback
        traceback.print_exc()
        return error_response('Failed to process multi-step try-on', 500)
