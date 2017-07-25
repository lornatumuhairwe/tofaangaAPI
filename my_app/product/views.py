import json
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask import request, jsonify, Blueprint, abort, session
from flask.views import MethodView
from my_app import db, app
from my_app.product.models import User, Bucketlist, BucketlistItem

catalog = Blueprint('catalog', __name__)
authentication = Blueprint('authentication', __name__)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(user_email):
    """Give user_id, return associated User object"""
    return User.query.get(user_email)


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
    user = User(email, password, name, birth_date)
    db.session.add(user)
    db.session.commit()
    return jsonify({user.id: {
        'name': user.name,
        'email': user.email,
        'birthdate': user.birth_date,
        'password': user.password
    }})


@authentication.route('/auth/login', methods=['POST', 'GET'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    #user = User(email, password)
    user = User.query.filter_by(email=email).first()
    if not user:
        #abort(404)
        res = {
            'message': 'User not found'
        }
    elif user.password == password:
       # session['logged_in'] = True
        res = {
            'name': user.name,
            'email': user.email,
            'birthdate': user.birth_date,
            'password': user.password
        }
        login_user(user)
    else:
        res = {
            'message': 'Password mismatch'
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
@login_required
def logout():
    #user = current_user
    logout_user()
    res = {
        'message': 'User logged'
    }
    return jsonify(res)
    #session.pop('logged_in', None)
    # email = request.form.get('email')
    # new_password = request.form.get('newpassword')
    # cnew_password = request.form.get('cnewpassword')
    # # user = User(email, password)
    # user = User.query.filter_by(email=email).first()
    # if not user:
    #     # abort(404)
    #     res = {
    #         'message': 'User not found'
    #     }
    # else:
    #     if new_password == cnew_password:
    #         user.password = new_password
    #         db.session.commit()
    #         res = {
    #             'name': user.name,
    #             'email': user.email,
    #             'birthdate': user.birth_date,
    #             'password': user.password
    #         }
    #return jsonify(res)

# class UserView(MethodView):
#
#     def get(self, id=None, page=1):
#         if not id:
#             users = User.query.paginate(page, 10).items
#             res = {}
#             for user in users:
#                 res[user.id] = {
#                         'name': user.name,
#                         'email': user.email,
#                         'birthdate': user.birth_date,
#                         'password': user.password,
#                     }
#         else:
#             user = User.query.filter_by(id=id).first()
#             if not user:
#                 abort(404)
#             res = {
#                 'name': user.name,
#                 'email': user.email,
#                 'birthdate': user.birth_date,
#                 'password': user.password
#             }
#         return jsonify(res)
#
#     def post(self):
#         name = request.form.get('name')
#         email = request.form.get('email')
#         birth_date = request.form.get('birthdate')
#         password = request.form.get('password')
#         user = User(email, password, name, birth_date )
#         db.session.add(user)
#         db.session.commit()
#         return jsonify({user.id: {
#             'name': user.name,
#             'email': user.email,
#             'birthdate': user.birth_date,
#             'password': user.password
#         }})
#     def put(self, id):
#         return
#
#     def delete(self, id):
#         return
#
# user_view = UserView.as_view('user_view')
# app.add_url_rule('/user/', view_func=user_view, methods=['GET', 'POST'])
# app.add_url_rule('/user/<int:id>', view_func=user_view, methods=['GET'])