import json
import uuid
from datetime import datetime
from utils.response import success_response, error_response, get_user_sub
from utils.dynamodb import put_item, get_item, query_items, delete_item
from utils.s3 import generate_presigned_get_url
from services.compositor import generate_mvp_composite

MAX_FITS = 20


def handler(event, context):
    """Handler for GET/POST /fit endpoint."""
    try:
        # Handle CORS preflight
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

        pk = f'USER#{user_sub}'

        # GET /fit/{fitId}
        if event.get('httpMethod') == 'GET' and event.get('pathParameters', {}).get('fitId'):
            fit_id = event['pathParameters']['fitId']
            sk = f'FIT#{fit_id}'
            fit = get_item(pk, sk)

            if not fit:
                return error_response('Fit not found', 404)

            image_url = None
            if fit.get('status') == 'READY' and fit.get('render_key'):
                image_url = generate_presigned_get_url(fit['render_key'], 3600)

            return success_response({
                'fitId': fit.get('fitId'),
                'status': fit.get('status'),
                'imageUrl': image_url,
                'items': fit.get('items', []),
                'createdAt': fit.get('createdAt'),
                'updatedAt': fit.get('updatedAt'),
            })

        # POST /fit
        if event.get('httpMethod') == 'POST':
            body = json.loads(event.get('body', '{}'))

            if not body.get('items') or not isinstance(body['items'], list) or len(body['items']) == 0:
                return error_response('Items array is required', 400)

            fit_id = str(uuid.uuid4())
            sk = f'FIT#{fit_id}'
            now = datetime.utcnow().isoformat()
            mode = body.get('mode', 'MVP_COMPOSITE')

            # Prune old fits if user has >= MAX_FITS
            existing_fits = query_items(pk, 'FIT#')
            if len(existing_fits) >= MAX_FITS:
                # Sort by createdAt and delete oldest
                sorted_fits = sorted(existing_fits, key=lambda x: x.get('createdAt', ''))
                to_delete = sorted_fits[:len(existing_fits) - MAX_FITS + 1]

                for old_fit in to_delete:
                    delete_item(old_fit['pk'], old_fit['sk'])

            # Create fit object
            fit = {
                'pk': pk,
                'sk': sk,
                'fitId': fit_id,
                'name': body.get('name'),
                'items': body['items'],
                'status': 'PENDING',
                'createdAt': now,
                'updatedAt': now,
            }

            # Remove None values
            fit = {k: v for k, v in fit.items() if v is not None}

            put_item(fit)

            # MVP mode: synchronous composition
            if mode == 'MVP_COMPOSITE':
                try:
                    render_key = generate_mvp_composite(
                        user_sub,
                        fit_id,
                        body['items'],
                        body.get('body_asset_key')
                    )

                    fit['status'] = 'READY'
                    fit['render_key'] = render_key
                    fit['updatedAt'] = datetime.utcnow().isoformat()
                    put_item(fit)

                    image_url = generate_presigned_get_url(render_key, 3600)
                    return success_response({
                        'fitId': fit_id,
                        'status': 'READY',
                        'imageUrl': image_url
                    })

                except Exception as e:
                    print(f'Composition failed: {e}')
                    fit['status'] = 'FAILED'
                    fit['updatedAt'] = datetime.utcnow().isoformat()
                    put_item(fit)
                    return success_response({'fitId': fit_id, 'status': 'FAILED'})

            # BEDROCK mode: Use Bedrock Nova Canvas for real virtual try-on
            elif mode == 'BEDROCK_NOVA':
                try:
                    from services.compositor import generate_bedrock_tryon

                    render_key = generate_bedrock_tryon(
                        user_sub,
                        fit_id,
                        body['items'],
                        body.get('body_asset_key')
                    )

                    fit['status'] = 'READY'
                    fit['render_key'] = render_key
                    fit['updatedAt'] = datetime.utcnow().isoformat()
                    put_item(fit)

                    image_url = generate_presigned_get_url(render_key, 3600)
                    return success_response({
                        'fitId': fit_id,
                        'status': 'READY',
                        'imageUrl': image_url,
                        'mode': 'BEDROCK_NOVA'
                    })

                except Exception as e:
                    print(f'Bedrock virtual try-on failed: {e}')
                    fit['status'] = 'FAILED'
                    fit['error'] = str(e)
                    fit['updatedAt'] = datetime.utcnow().isoformat()
                    put_item(fit)
                    return success_response({'fitId': fit_id, 'status': 'FAILED', 'error': str(e)})

            # Unknown mode
            return error_response(f'Unknown mode: {mode}', 400)

        return error_response('Method not allowed', 405)

    except Exception as e:
        print(f'Error handling fit: {e}')
        return error_response('Failed to handle fit', 500)
