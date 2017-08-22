from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.DevelopmentConfigs')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
from flask_cors import CORS, cross_origin
from flasgger import Swagger

from my_app.product.views import catalog, authentication
from my_app.product.bucketlist_views import bucketlist
from my_app.product.bucketlistitems_views import bucketlistitems
app.register_blueprint(catalog)
app.register_blueprint(authentication)
app.register_blueprint(bucketlist)
app.register_blueprint(bucketlistitems)

Swagger(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
db.create_all()