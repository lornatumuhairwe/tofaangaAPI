from .test_base import TestBase
import json
from my_app.product.models import User
from my_app import db


class TestUserAuth(TestBase):

    """ unit tests for user authentication """

    def test_error_handler(self):
        """ Ensure that 404 errors can be handled """
        return_value = self.app.get('/api/v1/bucketlis/', headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'The resource you have requested is not available')

    def test_whether_the_encode_auth_token_works(self):
        """ Ensure that authentication tokens are generated """
        user = User.query.filter_by(email="testi@mail.com").first()
        auth_token = user.encode_auth_token(user.id)  # encoding itself returns bytes
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        """ Ensure that authentication tokens can be decoded """
        user = User.query.filter_by(email="testi@mail.com").first()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(User.decode_auth_token(auth_token.decode('utf-8')) is 1)  # when you decode and pick up sub, you
        # pick the usr.id that is an Int

    def registration(self, email, password, birth_date=None, name=None):
        """ Function to simulate the user registration function """
        return self.app.post('/api/v1/auth/register', data=dict(
            email=email,
            password=password,
            birth_date=birth_date,
            name=name
        ))

    def test_register_new_user(self):
        """ Ensure that user registration is successful with correct credentials """
        return_value = self.registration('ltum@gmail.com', '1234')
        data = json.loads(return_value.data.decode())
        self.assertEqual('Registration Successful', data['message'])

    def test_validation_of_email_during_registration(self):
        """ Ensure that user registration is unsuccessful with incorrect credentials eg incorrect password"""
        return_value = self.registration('ltum', '1234')
        data = json.loads(return_value.data.decode())
        self.assertEqual('Invalid email', data['message'])

    def test_register_user_that_already_exists_return_error_message(self):
        """ Ensure that user registration is unsuccessful when the email exists already"""
        return_value = self.registration('testi@mail.com', '1234')
        data = json.loads(return_value.data.decode())
        self.assertEqual('User Exists in the records', data['message'])

    def test_register_user_without_an_email_or_password_return_error_message(self):
        """ Ensure that user registration is unsuccessful when email or password are not provided """
        return_value = self.registration('', '')
        data = json.loads(return_value.data.decode())
        self.assertEqual('Supply username and password', data['message'])
        return_value = self.registration('testi', '')
        data = json.loads(return_value.data.decode())
        self.assertEqual('Supply username and password', data['message'])
        return_value = self.registration('', 'testpass')
        data = json.loads(return_value.data.decode())
        self.assertEqual('Supply username and password', data['message'])

    def login(self, email, password):
        """ Function to test the login user endpoint """
        return self.app.post('/api/v1/auth/login', data=dict(
            email=email,
            password=password
        ))

    def test_login(self):
        """ Ensure that user registration is successful with correct credentials """
        return_value = self.login('testi@mail.com', 'testpass')
        data = json.loads(return_value.data.decode())
        self.assertEqual('successfully logged in', data['message'])
        self.assertEqual('success', data['status'])
        self.assertTrue(data['auth_token'])

    def test_login_with_invalid_email(self):
        """ Ensure that user registration is unsuccessful when email is not correct format """
        return_value = self.login('testi', 'testpass')
        data = json.loads(return_value.data.decode())
        self.assertEqual('Invalid email', data['message'])
        self.assertEqual(return_value.status_code, 400)

    def test_login_non_existent_user_return_error_message(self):
        """ Ensure that user registration is unsuccessful when credentials are not consistent with database records """
        return_value = self.login('lt@gmail.com', 'testpasser')
        data = json.loads(return_value.data.decode())
        self.assertEqual('User not found', data['message'])

    def test_login_with_incorrect_password(self):
        """ Ensure that user registration is unsuccessful when credentials are not consistent with database records """
        return_value = self.login('testi@mail.com', 'testpasser')
        data = json.loads(return_value.data.decode())
        self.assertEqual('Password mismatch', data['message'])
        self.assertEqual('fail', data['status'])

    def test_user_can_reset_password(self):
        """
        Ensure that resetting of password is successful for existing users with matching new password and confirmation.
        """
        return_value = self.app.post('/api/v1/auth/reset-password', data=dict(
            email=self.user.email,
            newpassword='1234',
            cnewpassword='1234'
        ))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'],'Password reset successful')

    def test_user_cannot_reset_password_for_a_user_that_doesnt_exist(self):
        """
        Ensure that resetting of password is unsuccessful for non existing users.
        """
        return_value = self.app.post('/api/v1/auth/reset-password', data=dict(
            email='lt@mail.com',
            newpassword='1234',
            cnewpassword='1234'
        ))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'],'User not found')

    def test_user_cannot_reset_password_for_a_user_with_invalid_email(self):
        """
        Ensure that resetting of password is unsuccessful when invalid email is passed.
        """
        return_value = self.app.post('/api/v1/auth/reset-password', data=dict(
            email='lt',
            newpassword='1234',
            cnewpassword='1234'
        ))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'],'Invalid email')

    def test_user_cannot_reset_password_when_the_confirmation_password_is_mismatched(self):
        """
        Ensure that resetting of password is unsuccessful if for existing users if
        new password and confirmation do not match.
        """
        return_value = self.app.post('/api/v1/auth/reset-password', data=dict(
            email=self.user.email,
            newpassword='12345',
            cnewpassword='1234'
        ))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'],"Confirmed password doesn't match password")

    def logout(self, token):
        """Function to test the user logout endpoint """
        return self.app.post('/api/v1/auth/logout',
                            headers=dict(Authorization=token))

    def test_logout_authenticated_users_only_else_return_error_message(self):
        """ Ensure that user with valid token gets logged out. """
        user = User('testi1@mail.com', 'testpass')
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token(user.id)
        return_value = self.logout(auth_token)
        self.assertTrue(auth_token)
        data = json.loads(return_value.data.decode())
        self.assertEqual('successfully logged out', data['status'])

    def test_return_error_message_when_unauthenticated_user_accesses_logout_route(self):
        """ Ensure that user with invalid token doesn't get logged out. """
        return_value = self.logout(None)
        data = json.loads(return_value.data.decode())
        self.assertEqual('Invalid token, Login again', data['message'])

    def test_cannot_logout_user_without_token(self):
        """ Ensure that user with invalid token doesn't get logged out. """
        return_value = self.app.post('/api/v1/auth/logout')
        data = json.loads(return_value.data.decode())
        self.assertEqual('Token not found, Login to get one', data['message'])
