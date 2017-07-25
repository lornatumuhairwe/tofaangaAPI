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

    def is_active(self):
        """True, as all users are active"""
        return True

    def get_id(self):
        """Return the email to satisfy Flask-Login's requirements"""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated"""
        return self.email

    def is_anonymous(self):
        """False, as anonymous users are not supported"""
        return False

    def __repr__(self):
        return '<User %r>' % self.email

class Bucketlist(db.Model):
    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id')) #has to be similar to the table name that it's coming from
    items = db.relationship('BucketlistItem', backref='bucketlist', lazy='dynamic')

    def __init__(self, name, owner_id, items):
        self.name = name
        self.owner = owner_id
        self.items = items

    def __repr__(self):
        return '<Bucketlist %r belongs to %r>' % (self.name, self.owner)

class BucketlistItem(db.Model):
    __tablename__ = 'BLitems'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    deadline = db.Column(db.String(20))
    status = db.Column(db.String(20))
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlists.id'))

    def __init__(self, title, deadline, status, bucketlist_id):
        self.title = title
        self.deadline = deadline
        self.status = status
        self.bucketlist = bucketlist_id

    def __repr__(self):
        return '<Item %r belongs to %r bucketlist>' % (self.title, self.bucketlist)