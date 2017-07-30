import json, flask
from my_app import db, app
from my_app.product.models import User, Bucketlist
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
        bucketlist = Bucketlist(name='Cities')
        db.session.add(bucketlist)
        user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        self.auth_token = user.encode_auth_token(user.id)
        self.app = app.test_client()
        self.user = user
        return self.app, self.auth_token, self.user

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

    def logout(self, token):
        return self.app.get('/auth/logout',
                            headers=dict(
                                Authorization=token
                                ))

    def test_logout_authenticated_users_only_else_return_error_message(self):
        rv = self.logout(self.auth_token)
        data = json.loads(rv.data.decode())
        self.assertEqual('successfully logged out', data['status'])

    def test_return_error_message_when_unauthenticated_user_accesses_logout_route(self):
        rv = self.logout('')
        data = json.loads(rv.data.decode())
        self.assertEqual('Token not found, Login to get one', data['message'])

    def create_bucketlist(self, bucketlist_name, token):
        return self.app.post('/bucketlists/', data=dict(
            name=bucketlist_name), headers=dict(Authorization=token))

    def test_user_can_add_bucketlist(self):
        rv = self.create_bucketlist('Oceans', self.auth_token)
        data = json.loads(rv.data.decode())
        self.assertEqual('Oceans',data['bucketlist'])

    def test_user_cannot_add_already_existing_bucketlist(self):
        rv = self.create_bucketlist('Cities', self.auth_token)
        data = json.loads(rv.data.decode())
        self.assertEqual('Bucketlist exists',data['message'])

    def test_unauthenticated_user_cannot_add_bucketlist(self):
        rv = self.create_bucketlist('Cities', None)
        data = json.loads(rv.data.decode())
        self.assertEqual('Invalid token, Login again',data['message'])

    def view_all_bucketlists(self, token):
        return self.app.get('/bucketlists/', headers=dict(
            Authorization=token
        ))

    def test_user_can_view_bucketlists(self):
        rv = self.view_all_bucketlists(self.auth_token)
        data = json.loads(rv.data.decode())
        self.assertEqual(data['1'], 'Cities')

    def test_unauthenticated_user_cannot_view_bucketlist(self):
        rv = self.view_all_bucketlists(None)
        data = json.loads(rv.data.decode())
        self.assertEqual('Invalid token, Login again',data['message'])

    with app.test_client() as c:
        rv = c.get('/bucketlists/?q=Cities')
        assert flask.request.args['q'] == 'Cities'
        assert flask.request.path == '/bucketlists/'
        # data = json.loads(rv.data.decode())
        # assert data['1'] == 'Cities'

    # def update_bucketlist(self, newname, token):
    #     return self.app.post('/bucketlists/<int:bucketlistID>', data=dict(
    #         newname=newname), headers=dict(
    #         Authorization=token
    #     ))
    # def test_user_can_update_bucketlist(self):
    #     bucketlist = Bucketlist(name='Career')
    #     db.session.add(bucketlist)
    #     self.user.bucketlists.append(bucketlist)  # FK relationship
    #     db.session.commit()
    #     rv = self.update_bucketlist('Work', self.auth_token)
    #     data = json.loads(rv.data.decode())
    #     self.assertEqual(data['2'], 'Work')



if __name__=='__main__':
    unittest.main()