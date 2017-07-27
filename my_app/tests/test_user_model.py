import json
from my_app import db, app
from my_app.product.models import User
#from my_app.product.views import login
import unittest

class TestUserModel(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config')
        db.session.close()
        db.drop_all()
        db.create_all()

    def test_lookup(self):
        user = User('test', 'testpass')
        db.session.add(user)
        db.session.commit()
        users = User.query.all()
        assert user in users
        print ("NUMBER OF ENTRIES:")
        print (len(users))

    def test_login_user_that_doesnt_exist(self):
        email = 'ltu@gmail.com'
        user = User.query.filter_by(email=email).first()




# class TestUserModel(unittest.TestCase):
#
#     def setUp(self):
#         self.app = app.test_client()
#
#     def login(self, email, password):
#         return self.app.post('/auth/login', data=json.dumps(dict(
#             email=email,
#             password=password
#         )),
#             content_type='application/json')
#
#     def test_encode_auth_token(self):
#         user = User.query.filter_by(email="ltu@gmail.com").first()
#         auth_token = user.encode_auth_token(user.id) # encoding itself returns bytes
#         self.assertTrue(isinstance(auth_token, bytes))
#
#     def test_decode_auth_token(self):
#         user = User.query.filter_by(email="ltu@gmail.com").first()
#         auth_token = user.encode_auth_token(user.id)
#         self.assertTrue(isinstance(auth_token, bytes))
#         self.assertTrue(User.decode_auth_token(auth_token.decode('utf-8')) is 4) #when you decode and pick up sub, you
#                                                                                 # pick the usr.id that is an Int
#
#     def test_login_user_doesnt_exist(self):
#         rv = self.login("ltuu@gmail.com", '1234')
#         data = json.loads(rv.data.decode())
#         assert 'User not found' in data['message']
#         self.assertEqual(data['code'], 401)
#
#     def test_login_user_enters_incorrect_password(self):
#         rv = self.login("ltu@gmail.com", '1234')
#         data = json.loads(rv.data.decode())
#         self.assertEqual('Password mismatch', data['message'])
#         self.assertEqual(data['code'], 401)
#         #self.assertEqual('fail', data['status'])

if __name__=='__main__':
    unittest.main()