from my_app import db


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
        return '<User %d>' % self.email

