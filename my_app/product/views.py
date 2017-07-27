import json
from flask import request, jsonify, Blueprint, abort, session, make_response
from my_app import db, app
from my_app.product.models import User, Bucketlist, BucketlistItem

catalog = Blueprint('catalog', __name__)
authentication = Blueprint('authentication', __name__)
bucketlist = Blueprint('bucketlist', __name__)

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
    user = User.query.filter_by(email=email).first()
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
                    'message': 'successfully logged in. ',
                    'code': 200,
                    'auth_token': auth_token.decode()
                }
                return jsonify(res)
        else:
            res = {
                'message': 'Password mismatch',
                'status': 'fail',
                'way forward': 'Try again. ',
                'code': 401
            }

            return jsonify(res)

@authentication.route('/auth/reset-password', methods=['POST', 'GET'])
def reset_password():
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
                'password': user.password
            }
            return jsonify(res)

@authentication.route('/auth/logout', methods=['POST', 'GET'])

def logout():

    auth_token = request.headers.get('Authorization')
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        #print (type(resp))
        if isinstance(resp, int):
        # if isinstance(resp, bytes):
            user = User.query.filter_by(id=resp).first()
            res = {
                'status': 'successfully logged out',
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

@bucketlist.route('/bucketlists/', methods=['POST', 'GET'])
def add_or_view_bucketlist():
    if request.method=='POST':
        name = request.form.get('name')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                user = User.query.filter_by(id=resp).first()
                item = Bucketlist.query.filter_by(name=name).first()
                if not item:
                    bucketlist = Bucketlist(name=name)
                    db.session.add(bucketlist)
                    user.bucketlists.append(bucketlist) # FK relationship
                    db.session.commit()
                    res = {
                        'buckelist': bucketlist.name
                    }
                else:
                    res = {
                        'message': 'Bucketlist exists'
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

    if request.method == 'GET':
        # name = request.form.get('name')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                res = {
                    bucketlist.id: bucketlist.name for bucketlist in Bucketlist.query.all()
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

@bucketlist.route('/bucketlists/<int:bucketlistID>', methods=['PUT','DELETE', 'GET'])
def view_update_delete_bucketlist(bucketlistID):
    if request.method=='PUT':
        newname = request.form.get('newname')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                bucketlist = Bucketlist.query.filter_by(id=bucketlistID).first()
                if bucketlist:
                    bucketlist.name = newname
                    db.session.commit()
                    res = {
                        bucketlist.id: bucketlist.name
                    }
                else:
                    res = {
                        'message': 'Bucketlist doesnt exist'
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

    if request.method == 'GET':
        # name = request.form.get('name')
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                bucketlist = Bucketlist.query.filter_by(id=bucketlistID).first()
                if bucketlist:
                    res = {
                        bucketlist.id: bucketlist.name
                    }
                else:
                    res = {
                        'message': 'Bucketlist doesnt exist'
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

    if request.method=='DELETE':
        auth_token = request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, int):
                bucketlist = Bucketlist.query.filter_by(id=bucketlistID).first()
                if bucketlist:
                    db.session.delete(bucketlist)
                    db.session.commit()
                    res = {
                        'message': 'Bucketlist deleted successfully'
                    }
                else:
                    res = {
                        'message': 'Bucketlist doesnt exist'
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