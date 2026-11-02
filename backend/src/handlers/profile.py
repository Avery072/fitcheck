import json
from datetime import datetime
from utils.response import success_response, error_response, get_user_sub
from utils.dynamodb import put_item, get_item


def handler(event, context):
    """Handler for GET/POST /profile endpoint."""
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
        
        print(f'Profile handler called with event: {json.dumps(event)}')
        user_sub = get_user_sub(event)
        print(f'Extracted user_sub: {user_sub}')
        if not user_sub:
            return error_response('Unauthorized', 401)

        pk = f'USER#{user_sub}'
        sk = 'PROFILE'

        # GET request - fetch profile
        if event.get('httpMethod') == 'GET':
            profile = get_item(pk, sk)
            return success_response({'profile': profile})

        # POST request - create/update profile
        if event.get('httpMethod') == 'POST':
            body = json.loads(event.get('body', '{}'))
            print(f'Profile POST request body: {json.dumps(body)}')

            # Auto-populate email from Cognito token if not provided
            if not body.get('email'):
                try:
                    # Extract email from Cognito claims
                    claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
                    if claims.get('email'):
                        body['email'] = claims['email']
                        print(f'Auto-populated email from token: {body["email"]}')
                except Exception as e:
                    print(f'Could not extract email from token: {e}')

            # Validate numeric ranges
            validations = [
                ('height_cm', 50, 300),
                ('weight_kg', 20, 500),
                ('chest_cm', 50, 200),
                ('waist_cm', 40, 200),
                ('hips_cm', 50, 200),
                ('inseam_cm', 40, 150),
            ]

            for field, min_val, max_val in validations:
                if field in body:
                    try:
                        value = float(body[field])
                        if value < min_val or value > max_val:
                            return error_response(
                                f'{field} must be between {min_val} and {max_val}',
                                400
                            )
                    except (ValueError, TypeError):
                        return error_response(f'{field} must be a number', 400)

            now = datetime.utcnow().isoformat()
            existing_profile = get_item(pk, sk)

            # Build profile object
            profile = {
                'pk': pk,
                'sk': sk,
                'email': body.get('email', existing_profile.get('email', '') if existing_profile else ''),
                'displayName': body.get('displayName'),
                'height_cm': body.get('height_cm'),
                'weight_kg': body.get('weight_kg'),
                'chest_cm': body.get('chest_cm'),
                'waist_cm': body.get('waist_cm'),
                'hips_cm': body.get('hips_cm'),
                'inseam_cm': body.get('inseam_cm'),
                'preferred_fit': body.get('preferred_fit'),
                'avatar_key': body.get('avatar_key'),
                'body_asset_key': body.get('body_asset_key', existing_profile.get('body_asset_key') if existing_profile else None),
                'face_asset_key': body.get('face_asset_key', existing_profile.get('face_asset_key') if existing_profile else None),
                'createdAt': existing_profile.get('createdAt', now) if existing_profile else now,
                'updatedAt': now,
            }

            # Remove None values
            profile = {k: v for k, v in profile.items() if v is not None}

            put_item(profile)
            return success_response({'ok': True, 'profile': profile})

        return error_response('Method not allowed', 405)

    except Exception as e:
        print(f'Error handling profile: {e}')
        import traceback
        print(f'Traceback: {traceback.format_exc()}')
        return error_response(f'Failed to handle profile: {str(e)}', 500)
