import json
from my_app import db, app
from my_app.product.models import User
from my_app.product.views import login
import unittest


class TestUserModel(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def login(self, username, password):
        return self.app.post('/auth/login', data=json.dumps(dict(
            username=username,
            password=password
        )),
        content_type='application/json',
                             )

    # def logout(self):
    #     return s
    def test_encode_auth_token(self):
        user = User.query.filter_by(email="ltu@gmail.com").first()
        auth_token = user.encode_auth_token(user.id) # encoding itself returns bytes
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        user = User.query.filter_by(email="ltu@gmail.com").first()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(User.decode_auth_token(auth_token.decode('utf-8')) is 4) #when you decode and pick up sub, you
                                                                                # pick the usr.id that is an Int

    def test_login(self):
        rv = self.login("ltuu@gmail.com", '1234')
        data = json.loads(rv.data.decode())
        assert 'User not found' in data['message']
        self.assertEqual(data['code'], 404)

if __name__=='__main__':
    unittest.main()