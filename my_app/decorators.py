from functools import wraps
from my_app.product.models import User
from flask import request, jsonify


def authenticate(auth):
    wraps(auth)

    def inner_method(*args, **kwargs):
        if "Authorization" in request.headers:
            auth_token = request.headers.get('Authorization')
            user_id = User.decode_auth_token(auth_token)
            if isinstance(user_id, int):
                kwargs['user_id'] = user_id
                # kwargs['auth_token'] = auth_token
                return auth(*args, **kwargs)
            else:
                res = {
                    'status': 'fail',
                    'message': 'Invalid token, Login again'
                }
                return jsonify(res), 401
        else:
            res = {
                'status': 'fail',
                'message': 'Token not found, Login to get one'
            }
            return jsonify(res), 401
    inner_method.__doc__ = auth.__doc__
    return inner_method
