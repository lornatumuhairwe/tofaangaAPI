from flask import request, jsonify, Blueprint
from my_app import db
from my_app.product.models import User, BlacklistToken

# swagger = Swagger(app)
catalog = Blueprint('catalog', __name__)
authentication = Blueprint('authentication', __name__)


@catalog.route('/')
@catalog.route('/home')
def home():
    return "Welcome to the User Home"


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
                  description: "Registration Failed"
                401:
                  description: " email exists in the database"
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

    elif not user:
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

    else:
        res = {
            'message': 'User Exists in the records'
        }

    return jsonify(res)


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
                      description: "Login Failed"
                    401:
                      description: "Login doesn't exist"
               """
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    #print (user.email)
    if not user:
        #abort(404)
        res = {
            'message': 'User not found',
            'code': 401
        }
        return jsonify(res)
    else:
        if user.password == password:
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                res = {
                    'status': 'success',
                    'message': 'successfully logged in',
                    'code': 200,
                    'auth_token': auth_token.decode()
                }
                return jsonify(res)
        else:
            res = {
                'message': 'Password mismatch',
                'status': 'fail',
                'code': 401
            }

            return jsonify(res)


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
                      description: "Password reset Failed"
                    401:
                      description: "Password reset doesn't exist"
               """
    email = request.form.get('email')
    new_password = request.form.get('newpassword')
    cnew_password = request.form.get('cnewpassword')
    user = User.query.filter_by(email=email).first()
    if not user:
        # abort(404)
        res = {
            'message': 'User not found'
        }
        return jsonify(res)
    else:
        if new_password == cnew_password:
            user.password = new_password
            db.session.commit()
            res = {
                'name': user.name,
                'email': user.email,
                'birthdate': user.birth_date,
                'password': user.password,
                'message': 'Password reset successful'
            }
        else:
            res = {
                'message': "Confirmed password doesn't match password"
            }

        return jsonify(res)


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
                  description: "Logout Failed"
                401:
                  description: "Logout doesn't exist"
           """
    auth_token = request.headers.get('Authorization')
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if isinstance(resp, int):
            #if resp = users ID, then the auth_token should be destroyed.
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
            except Exception as e:
                res = {
                    'status': 'fail',
                    'message': e
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
