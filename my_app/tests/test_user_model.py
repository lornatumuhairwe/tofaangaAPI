from .test_base import TestBase
import json
from my_app.product.models import User
from my_app import db


class TestUserModel(TestBase):

    def test_error_handler(self):
        rv1 = self.app.get('/api/v1/bucketlis/', headers=dict(Authorization=self.auth_token))
        data1 = json.loads(rv1.data.decode())
        self.assertEqual(data1['message'], 'The resource you have requested is not available')

    def test_whether_the_encode_auth_token_works(self):
        user = User.query.filter_by(email="testi@mail.com").first()
        auth_token = user.encode_auth_token(user.id)  # encoding itself returns bytes
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        user = User.query.filter_by(email="testi@mail.com").first()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(User.decode_auth_token(auth_token.decode('utf-8')) is 1) #when you decode and pick up sub, you
                                                                                  # pick the usr.id that is an Int

    def registration(self, email, password, birth_date=None, name=None):
        return self.app.post('/api/v1/auth/register', data=dict(
            email=email,
            password=password,
            birth_date=birth_date,
            name=name
        ))

    def test_register_new_user(self):
        rv = self.registration('ltum@gmail.com', '1234')
        data = json.loads(rv.data.decode())
        self.assertEqual('Registration Successful', data['message'])

    def test_validation_of_email_during_registration(self):
        rv = self.registration('ltum', '1234')
        data = json.loads(rv.data.decode())
        self.assertEqual('Invalid email', data['message'])

    def test_register_user_that_already_exists_return_error_message(self):
        rv = self.registration('testi@mail.com', '1234')
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
        return self.app.post('/api/v1/auth/login', data=dict(
            email=email,
            password=password
        ))

    def test_login(self):
        rv = self.login('testi@mail.com', 'testpass')
        data = json.loads(rv.data.decode())
        self.assertEqual('successfully logged in', data['message'])
        self.assertEqual('success', data['status'])
        self.assertTrue(data['auth_token'])

    def test_login_non_existent_user_return_error_message(self):
        rv = self.login('lt@gmail.com', 'testpasser')
        data = json.loads(rv.data.decode())
        assert 'User not found' in data['message']

    def test_login_with_incorrect_password(self):
        rv = self.login('testi@mail.com', 'testpasser')
        data = json.loads(rv.data.decode())
        self.assertEqual('Password mismatch', data['message'])
        self.assertEqual('fail', data['status'])

    def test_user_can_reset_password(self):
        rv = self.app.post('/api/v1/auth/reset-password', data=dict(
            email=self.user.email,
            newpassword='1234',
            cnewpassword='1234'
        ))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'],'Password reset successful')

    def test_user_cannot_reset_password_for_a_user_that_doesnt_exist(self):
        rv = self.app.post('/api/v1/auth/reset-password', data=dict(
            email='lt@mail.com',
            newpassword='1234',
            cnewpassword='1234'
        ))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'],'User not found')

    def test_user_cannot_reset_password_when_the_confirmation_password_is_mismatched(self):
        rv = self.app.post('/api/v1/auth/reset-password', data=dict(
            email=self.user.email,
            newpassword='12345',
            cnewpassword='1234'
        ))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'],"Confirmed password doesn't match password")

    def logout(self, token):
        return self.app.post('/api/v1/auth/logout',
                            headers=dict(Authorization=token))

    def test_logout_authenticated_users_only_else_return_error_message(self):
        user = User('testi1@mail.com', 'testpass')
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token(user.id)
        rv = self.logout(auth_token)
        self.assertTrue(auth_token)
        data = json.loads(rv.data.decode())
        self.assertEqual('successfully logged out', data['status'])

    def test_return_error_message_when_unauthenticated_user_accesses_logout_route(self):
        rv = self.logout(None)
        data = json.loads(rv.data.decode())
        self.assertEqual('Invalid token, Login again', data['message'])

    def test_cannot_logout_user_without_token(self):
        rv = self.app.post('/api/v1/auth/logout')
        data = json.loads(rv.data.decode())
        self.assertEqual('Token not found, Login to get one', data['message'])
