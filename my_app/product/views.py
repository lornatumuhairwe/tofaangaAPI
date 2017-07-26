import json
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask import request, jsonify, Blueprint, abort, session, make_response
from flask.views import MethodView
from my_app import db, app
from my_app.product.models import User, Bucketlist, BucketlistItem

catalog = Blueprint('catalog', __name__)
authentication = Blueprint('authentication', __name__)

login_manager = LoginManager()
login_manager.init_app(app)


# @login_manager.user_loader
# def user_loader(user_email):
#     """Give user_id, return associated User object"""
#     return User.query.get(user_email)


@catalog.route('/')
@catalog.route('/home')
def home():
    return "Welcome to the User Home"


@authentication.route('/auth/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    birth_date = request.form.get('birthdate')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email, password, name, birth_date)
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token(user.id)
        res = {user.id: {
            'name': user.name,
            'email': user.email,
            'birthdate': user.birth_date,
            'password': user.password,
            'auth_token': auth_token.decode()
        }}

    else:
        res = {
            'message': 'User Exists in the records'
        }

    return jsonify(res)


@authentication.route('/auth/login', methods=['POST', 'GET'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    #user = User(email, password)
    user = User.query.filter_by(email=email).first()
    if not user:
        #abort(404)
        res = {
            'message': 'User not found',
            'code': 404
        }
    elif user.password == password:
        auth_token = user.encode_auth_token(user.id)
        if auth_token:
            res = {
                'status': 'success',
                'message': 'successfully logged in. ',
                'code': 200,
                'auth_token': auth_token.decode()
            }
    else:
        res = {
            'message': 'Password mismatch',
            'status': 'fail',
            'way forward': 'Try again. ',
            'code': 500
}

    return jsonify(res)

@authentication.route('/auth/reset-password', methods=['POST', 'GET'])
def reset_password():
    email = request.form.get('email')
    new_password = request.form.get('newpassword')
    cnew_password = request.form.get('cnewpassword')
    # user = User(email, password)
    user = User.query.filter_by(email=email).first()
    if not user:
        # abort(404)
        res = {
            'message': 'User not found'
        }
    else:
        if new_password == cnew_password:
            user.password = new_password
            db.session.commit()
            res = {
                'name': user.name,
                'email': user.email,
                'birthdate': user.birth_date,
                'password': user.password
            }
    return jsonify(res)

@authentication.route('/auth/logout', methods=['POST', 'GET'])
#@login_required
def logout():
    #user = current_user
    #logout_user()
    # res = {
    #     'message': 'User logged'
    # }
    auth_token = request.headers.get('Authorization')
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        print (type(resp))
        if isinstance(resp, int):
        # if isinstance(resp, bytes):
            user = User.query.filter_by(id=resp).first()
            res = {
                'status': 'success',
                'data': {
                    'user_id': user.id,
                    'email': user.email
                }
            }
        else:
            res = {
                'status': 'fail',
                'message': 'Invalid token, Login again'
            }
    else:
        res = {
            'status': 'fail',
            'message': 'Token not found, Login to get one'
        }
    return jsonify(res)