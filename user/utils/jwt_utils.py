import jwt
from django.contrib.auth import authenticate
from jwt.algorithms import RSAAlgorithm
from rest_framework_jwt.settings import api_settings


# Cognito token decoder
def cognito_jwt_decoder(token):
    options = {'verify_exp': api_settings.JWT_VERIFY_EXPIRATION}
    # JWT  토큰을 decode 함
    unverified_header = jwt.get_unverified_header(token)
    if 'kid' not in unverified_header:
        raise jwt.DecodeError('Incorrect Authentication credentials')

    kid = unverified_header['kid']
    try:
        public_key = RSAAlgorithm.from_jwk(api_settings.JWT_PUBLIC_KEY[kid])
    except KeyError:
        raise jwt.DecodeError('Can\'t find Proper public key in jwks')
    else:
        decoded_token = jwt.decode(
            token,
            public_key,
            api_settings.JWT_VERIFY,
            options=options,
            leeway=api_settings.JWT_LEEWAY,
            audience=api_settings.JWT_AUDIENCE,
            issuer=api_settings.JWT_ISSUER,
            algorithms=[api_settings.JWT_ALGORITHM]
        )
        return decoded_token


# user login or create user
def user_info_handler(payload):
    username = payload.get('sub')
    authenticate(remote_user=username)
    return username
