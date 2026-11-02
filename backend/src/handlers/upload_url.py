import uuid
from utils.response import success_response, error_response, get_user_sub
from utils.s3 import generate_presigned_put_url


def handler(event, context):
    """Handler for GET /upload-url endpoint."""
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

        # Get type and file extension from query parameters
        query_params = event.get('queryStringParameters') or {}
        upload_type = query_params.get('type', 'other')
        file_extension = query_params.get('extension', 'png')
        
        # Validate file extension
        allowed_extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp']
        if file_extension.lower() not in allowed_extensions:
            return error_response(f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}', 400)
        
        # Determine content type based on extension
        content_type_map = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        content_type = content_type_map.get(file_extension.lower(), 'image/png')

        # Generate unique asset ID and S3 key
        asset_id = str(uuid.uuid4())
        key = f'user-assets/{user_sub}/{asset_id}.{file_extension.lower()}'

        # Generate presigned PUT URL
        url = generate_presigned_put_url(key, content_type, 300)

        return success_response({
            'url': url,
            'key': key,
            'assetId': asset_id,
        })

    except Exception as e:
        print(f'Error generating upload URL: {e}')
        return error_response('Failed to generate upload URL', 500)
