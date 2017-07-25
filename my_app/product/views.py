import json
from flask import request, jsonify, Blueprint, abort
from flask.views import MethodView
from my_app import db, app
from my_app.product.models import User

catalog = Blueprint('catalog', __name__)


@catalog.route('/')
@catalog.route('/home')
def home():
    return "Welcome to the User Home"


class UserView(MethodView):

    def get(self, id=None, page=1):
        if not id:
            users = User.query.paginate(page, 10).items
            res = {}
            for user in users:
                res[user.id] = {
                        'name': user.name,
                        'email': user.email,
                        'birthdate': user.birth_date,
                        'password': user.password,
                    }
        else:
            user = User.query.filter_by(id=id).first()
            if not user:
                abort(404)
            res = {
                'name': user.name,
                'email': user.email,
                'birthdate': user.birth_date,
                'password': user.password
            }
        return jsonify(res)

    def post(self):
        name = request.form.get('name')
        email = request.form.get('email')
        birth_date = request.form.get('birthdate')
        password = request.form.get('password')
        user = User(email, password, name, birth_date )
        db.session.add(user)
        db.session.commit()
        return jsonify({user.id: {
            'name': user.name,
            'email': user.email,
            'birthdate': user.birth_date,
            'password': user.password
        }})
    def put(self, id):
        return

    def delete(self, id):
        return

user_view = UserView.as_view('user_view')
app.add_url_rule('/user/', view_func=user_view, methods=['GET', 'POST'])
app.add_url_rule('/user/<int:id>', view_func=user_view, methods=['GET'])