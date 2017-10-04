import unittest
from my_app import db, app, bcrypt
from my_app.product.models import User, Bucketlist


class TestBase(unittest.TestCase):

    """
    Before each test is run, the database tables are created ,a test user is added with one bucketlist.
    Database Tables are dropped after the test has been run.
    """

    def setUp(self):
        app.config.from_object('config.TestingConfigs')
        db.create_all()
        user = User('testi@mail.com', bcrypt.generate_password_hash('testpass').decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        bucketlist = Bucketlist(name='Cities')
        db.session.add(bucketlist)
        user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        self.bucketlistID = bucketlist.id
        self.auth_token = user.encode_auth_token(user.id)
        self.app = app.test_client()
        self.user = user
        return self.app, self.auth_token, self.user, self.bucketlistID

    def tearDown(self):
        db.session.close()
        db.drop_all()


