from my_app import db, app
import jwt
import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    birth_date = db.Column(db.String(10))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    bucketlists = db.relationship('Bucketlist', backref='user', lazy='dynamic')

    def __init__(self, email, password, name=None, birth_date=None):
        self.email = email
        self.password = password
        self.name = name
        self.birth_date = birth_date


    def __repr__(self):
        return '<User %r>' % self.email

    def encode_auth_token(self, user_id):
        """Generate the Auth token, return: string"""
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=1000),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }

            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), algorithms='HS256')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            print('Signature expired. Please log in again')
            return 'Signature expired. Please log in again'
        except jwt.InvalidTokenError:
            print('Invalid token. Please log in again')
            return 'Invalid token. Please login again.'


class Bucketlist(db.Model):
    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id')) #has to be similar to the table name that it's coming from
    items = db.relationship('BucketlistItem', backref='bucketlist', lazy='dynamic')

    # def __init__(self, name, owner_id):
    #     self.name = name
    #     self.owner = owner_id
    #     print('Printing owner from models'+ str(self.owner))

    def __init__(self, name):
        self.name = name
        # print('Printing owner from models'+ str(self.owner))

    def __repr__(self):
        return '<Bucketlist %r belongs>' % (self.name)

class BucketlistItem(db.Model):
    __tablename__ = 'BLitems'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    deadline = db.Column(db.String(20))
    status = db.Column(db.String(20))
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlists.id'))

    def __init__(self, title, deadline, status):
        self.title = title
        self.deadline = deadline
        self.status = status

    def __repr__(self):
        return '<Item %r belongs to>' % (self.title)