from utils.response import success_response, error_response, get_user_sub
from utils.dynamodb import query_items
from utils.s3 import generate_presigned_get_url


def handler(event, context):
    """Handler for GET /fits endpoint."""
    try:
        user_sub = get_user_sub(event)
        if not user_sub:
            return error_response('Unauthorized', 401)

        pk = f'USER#{user_sub}'
        fits = query_items(pk, 'FIT#')

        # Sort by createdAt descending, limit to 20 newest
        sorted_fits = sorted(fits, key=lambda x: x.get('createdAt', ''), reverse=True)[:20]

        result = []
        for fit in sorted_fits:
            thumbnail_url = None
            if fit.get('status') == 'READY' and fit.get('render_key'):
                thumbnail_url = generate_presigned_get_url(fit['render_key'], 3600)

            result.append({
                'fitId': fit.get('fitId'),
                'name': fit.get('name'),
                'thumbnailUrl': thumbnail_url,
                'createdAt': fit.get('createdAt'),
                'status': fit.get('status'),
            })

        return success_response({'fits': result})

    except Exception as e:
        print(f'Error fetching fits: {e}')
        return error_response('Failed to fetch fits', 500)
