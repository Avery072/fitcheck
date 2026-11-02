import json
import os
import urllib.request
import urllib.parse
from utils.response import success_response, error_response


def handler(event, context):
    """Handler for POST /token endpoint (PKCE token exchange)."""
    try:
        body = json.loads(event.get('body', '{}'))

        if not body.get('code') or not body.get('redirectUri'):
            return error_response('Missing required fields', 400)

        cognito_domain = os.environ.get('COGNITO_DOMAIN')
        client_id = os.environ.get('COGNITO_CLIENT_ID')

        # Exchange code for tokens using PKCE
        token_endpoint = f'{cognito_domain}/oauth2/token'
        params = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'code': body['code'],
            'redirect_uri': body['redirectUri'],
            'code_verifier': body['codeVerifier'],
        }

        data = urllib.parse.urlencode(params).encode('utf-8')
        req = urllib.request.Request(
            token_endpoint,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        try:
            with urllib.request.urlopen(req) as response:
                tokens = json.loads(response.read().decode('utf-8'))

            return success_response({
                'id_token': tokens.get('id_token'),
                'access_token': tokens.get('access_token'),
                'refresh_token': tokens.get('refresh_token'),
                'expiresIn': tokens.get('expires_in'),
            })

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f'Token exchange failed: {error_body}')
            return error_response('Token exchange failed', e.code)

    except Exception as e:
        print(f'Error exchanging token: {e}')
        return error_response('Failed to exchange token', 500)
