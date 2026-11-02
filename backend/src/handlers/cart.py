import json
from datetime import datetime
from decimal import Decimal
from utils.response import success_response, error_response, get_user_sub
from utils.dynamodb import put_item, query_items


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
    """Handler for GET/POST /cart endpoint."""
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

        pk = f'USER#{user_sub}'

        # GET request - fetch cart items
        if event.get('httpMethod') == 'GET':
            items = query_items(pk, 'CARTITEM#')
            # Convert Decimal objects to regular numbers
            items = convert_decimals(items)
            return success_response({'items': items})

        # POST request - add/update cart item
        if event.get('httpMethod') == 'POST':
            body = json.loads(event.get('body', '{}'))

            # Validate required fields
            if not body.get('retailer') or not body.get('productId') or not body.get('title'):
                return error_response('Missing required fields', 400)

            sk = f'CARTITEM#{body["retailer"]}#{body["productId"]}'
            now = datetime.utcnow().isoformat()

            cart_item = {
                'pk': pk,
                'sk': sk,
                'retailer': body['retailer'],
                'productId': body['productId'],
                'title': body['title'],
                'price_cents': body.get('price_cents', 0),
                'currency': body.get('currency', 'USD'),
                'productUrl': body.get('productUrl', ''),
                'imageUrl': body.get('imageUrl', ''),
                'selectedSize': body.get('selectedSize'),
                'color': body.get('color'),
                'category': body.get('category'),
                'addedAt': now,
            }

            # Remove None values
            cart_item = {k: v for k, v in cart_item.items() if v is not None}

            put_item(cart_item)
            return success_response({'ok': True})

        # DELETE request - remove cart item
        if event.get('httpMethod') == 'DELETE':
            query_params = event.get('queryStringParameters') or {}
            retailer = query_params.get('retailer')
            product_id = query_params.get('productId')
            
            if not retailer or not product_id:
                return error_response('retailer and productId parameters required', 400)
            
            sk = f'CARTITEM#{retailer}#{product_id}'
            
            # Delete item from DynamoDB
            from utils.dynamodb import delete_item
            delete_item(pk, sk)
            
            return success_response({'ok': True})

        return error_response('Method not allowed', 405)

    except Exception as e:
        print(f'Error handling cart: {e}')
        return error_response('Failed to handle cart', 500)
