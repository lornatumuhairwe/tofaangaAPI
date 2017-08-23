from flask import request, jsonify, Blueprint
from my_app import db, app
from my_app import bcrypt
from my_app.product.models import User, BlacklistToken
import re

# swagger = Swagger(app)
catalog = Blueprint('catalog', __name__)
authentication = Blueprint('authentication', __name__)


@catalog.route('/')
def home():
    return "Welcome to the User Home"

@app.errorhandler(404)
def page_not_found(e):
    res = {
        "message": "The resource you have requested is not available"
    }
    return jsonify(res), 404


@authentication.route('/auth/register', methods=['POST'])
def register():
    """ Registration of a new user
            ---
            tags:
            - "Authentication operations"
            consumes:
                - "multipart/form-data"
            produces:
                - "application/json"
            parameters:
            - name: "email"
              in: "formData"
              description: "Email of new user"
              required: true
              type: "string"
            - name: "password"
              in: "formData"
              description: "Password of new user"
              required: true
              type: "string"
            - name: "name"
              in: "formData"
              description: "Name of new user"
              required: false
              type: "string"
            - name: "birthdate"
              in: "formData"
              description: "Birthdate of new user"
              required: false
              type: "string"
            responses:
                200:
                  description: "Registration Successful"
                400:
                  description: "Registration Failed. Bad request, use appropriate parameters"
           """
    name = request.form.get('name')
    email = request.form.get('email')
    birth_date = request.form.get('birthdate')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if not email or not password:
        res = {
            'message': 'Supply username and password'
        }

        return jsonify(res), 400

    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        res = {
            'message': 'Invalid email'
        }

        return jsonify(res), 400

    elif not user:
        password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(email, password, name, birth_date)
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token(user.id)
        res = {
            'user id': user.id,
            'name': user.name,
            'email': user.email,
            'birthdate': user.birth_date,
            'password': user.password,
            'auth_token': auth_token.decode(),
            'message': 'Registration Successful'
        }

        return jsonify(res), 200

    else:
        res = {
            'message': 'User Exists in the records'
        }

        return jsonify(res), 400


@authentication.route('/auth/login', methods=['POST'])
def login():
    """ Login user
                ---
                tags:
                - "Authentication operations"
                consumes:
                    - "multipart/form-data"
                produces:
                    - "application/json"
                parameters:
                - name: "email"
                  in: "formData"
                  description: "Email of user"
                  required: true
                  type: "string"
                - name: "password"
                  in: "formData"
                  description: "Password of user"
                  required: true
                  type: "string"
                responses:
                    200:
                      description: "Login Successful"
                    400:
                      description: "Login Failed. Bad request, use appropriate parameters "
               """
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        res = {
            'message': 'Invalid email'
        }

        return jsonify(res), 400
    # print (user.email)
    elif not user:
        # abort(404)
        res = {
            'message': 'User not found',
        }
        return jsonify(res), 400
    else:
        if bcrypt.check_password_hash(user.password, password):
        # if user.password == password:
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                res = {
                    'status': 'success',
                    'message': 'successfully logged in',
                    'auth_token': auth_token.decode()
                }
                return jsonify(res), 200
        else:
            res = {
                'message': 'Password mismatch',
                'status': 'fail'
            }

            return jsonify(res), 400


@authentication.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """ Reset user Password
                ---
                tags:
                - "Authentication operations"
                consumes:
                    - "multipart/form-data"
                produces:
                    - "application/json"
                parameters:
                - name: "email"
                  in: "formData"
                  description: "Email of user"
                  required: true
                  type: "string"
                - name: "newpassword"
                  in: "formData"
                  description: "New password of user"
                  required: true
                  type: "string"
                - name: "cnewpassword"
                  in: "formData"
                  description: "Enter new password of user again"
                  required: true
                  type: "string"
                responses:
                    200:
                      description: "Password reset Successful"
                    400:
                      description: "Password reset Failed. Bad request, use appropriate parameters"
               """
    email = request.form.get('email')
    new_password = request.form.get('newpassword')
    cnew_password = request.form.get('cnewpassword')
    user = User.query.filter_by(email=email).first()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        res = {
            'message': 'Invalid email'
        }

        return jsonify(res), 400
    elif not user:
        # abort(404)
        res = {
            'message': 'User not found'
        }
        return jsonify(res), 400
    else:
        if new_password == cnew_password:
            user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            res = {
                'name': user.name,
                'email': user.email,
                'birthdate': user.birth_date,
                'password': user.password,
                'message': 'Password reset successful'
            }
            return jsonify(res), 200
        else:
            res = {
                'message': "Confirmed password doesn't match password"
            }

            return jsonify(res), 400


@authentication.route('/auth/logout', methods=['POST'])
def logout():
    """ User Logout
            ---
            tags:
            - "Authentication operations"
            consumes:
                - "application/json"
            produces:
                - "application/json"
            parameters:
            - name: "Authorization"
              in: "header"
              description: "Token of a logged in user"
              required: true
              type: "string"
            responses:
                200:
                  description: "Logout Successful"
                400:
                  description: "Logout Failed. Bad request, use appropriate parameters"
                401:
                  description: "Logout Failed. Invalid token, Login again or Token not found, Login to get one"
           """
    auth_token = request.headers.get('Authorization')
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if isinstance(resp, int):
            # if resp = users ID, then the auth_token should be destroyed.
            blacklist_token = BlacklistToken(token=auth_token)
            try:
                db.session.add(blacklist_token)
                db.session.commit()
                user = User.query.filter_by(id=resp).first()
                res = {
                    'status': 'successfully logged out',
                    'data': {
                        'user_id': user.id,
                        'email': user.email
                    }}
                return jsonify(res), 200

            except Exception as e:
                res = {
                    'status': 'fail',
                    'message': e
                }
                return jsonify(res), 400
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
