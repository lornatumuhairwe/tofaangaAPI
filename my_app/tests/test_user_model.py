import json
from my_app import db, app
from my_app.product.models import User
import unittest

class TestUserModel(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfigs')
        db.session.close()
        db.drop_all()
        db.create_all()
        user = User('testi', 'testpass')
        db.session.add(user)
        db.session.commit()
        self.app = app.test_client()
        return self.app

    def test_whether_the_encode_auth_token_works(self):
        user = User.query.filter_by(email="testi").first()
        auth_token = user.encode_auth_token(user.id) # encoding itself returns bytes
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        user = User.query.filter_by(email="testi").first()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(User.decode_auth_token(auth_token.decode('utf-8')) is 1) #when you decode and pick up sub, you
                                                                                  # pick the usr.id that is an Int

    def registration(self, email, password, birth_date=None, name=None):
        return self.app.post('/auth/register', data=dict(
            email=email,
            password=password,
            birth_date=birth_date,
            name=name
        ))

    def test_register_new_user(self):
        rv = self.registration('ltum@gmail.com', '1234')
        data = json.loads(rv.data.decode())
        self.assertEqual('Registration Successful', data['message'])

    def test_register_user_that_already_exists_return_error_message(self):
        rv = self.registration('testi', '1234')
        data = json.loads(rv.data.decode())
        self.assertEqual('User Exists in the records', data['message'])

    def test_register_user_without_an_email_or_password_return_error_message(self):
        rv = self.registration('', '')
        data = json.loads(rv.data.decode())
        self.assertEqual('Supply username and password', data['message'])
        rv = self.registration('testi', '')
        data = json.loads(rv.data.decode())
        self.assertEqual('Supply username and password', data['message'])
        rv = self.registration('', 'testpass')
        data = json.loads(rv.data.decode())
        self.assertEqual('Supply username and password', data['message'])

    def login(self, email, password):
        return self.app.post('/auth/login', data=dict(
            email=email,
            password=password
        ))

    def test_login(self):
        rv = self.login('testi', 'testpass')
        data = json.loads(rv.data.decode())
        self.assertEqual('successfully logged in', data['message'])

    def test_login_non_existent_user_return_error_message(self):
        rv = self.login('lt@gmail.com', 'testpasser')
        data = json.loads(rv.data.decode())
        assert 'User not found' in data['message']
        self.assertEqual(data['code'], 401)

    def test_login_with_incorrect_password(self):
        rv = self.login('testi', 'testpasser')
        data = json.loads(rv.data.decode())
        self.assertEqual('Password mismatch', data['message'])
        self.assertEqual(data['code'], 401)
        self.assertEqual('fail', data['status'])

if __name__=='__main__':
    unittest.main()