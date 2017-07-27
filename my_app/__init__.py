from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
db = SQLAlchemy(app)


from my_app.product.views import catalog, authentication, bucketlist
app.register_blueprint(catalog)
app.register_blueprint(authentication)
app.register_blueprint(bucketlist)

db.create_all()