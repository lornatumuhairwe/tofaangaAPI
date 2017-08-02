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
        # print('---------***************---------------------')
        self.bucketlistID = bucketlist.id
        self.auth_token = user.encode_auth_token(user.id)
        self.app = app.test_client()
        self.user = user
        return self.app, self.auth_token, self.user, self.bucketlistID

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
        return self.app.post('/auth/logout',
                            headers=dict(Authorization=token))

    def test_logout_authenticated_users_only_else_return_error_message(self):
        user = User('testi1', 'testpass')
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token(user.id)
        rv = self.logout(auth_token)
        self.assertTrue(auth_token)
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
        data = json.loads(rv.data.decode())

    def test_pagination(self):
        rv = self.app.get('/bucketlists/?limit=2', headers=dict(
            Authorization=self.auth_token
        ))
        data = json.loads(rv.data.decode())
        self.assertEqual(1, len(data))

    def test_name_based_search_of_bucketlist(self):
        rv = self.app.get('/bucketlists/?q=Cities', headers=dict(
            Authorization=self.auth_token
        ))
        data = json.loads(rv.data.decode())
        self.assertTrue(data['1'])

    def test_get_existing_bucketlist(self):
        rv = self.app.get('/bucketlists/1', headers=dict(
            Authorization=self.auth_token
        ))
        data = json.loads(rv.data.decode())
        self.assertTrue(data['1'])

    def test_authenticated_user_can_update_bucketlist(self):
        bucketlist = Bucketlist(name='Career')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.put('/bucketlists/'+ str(bucketlistID), data=json.dumps(dict(newname='Work')),headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist updated successfully')

    def test_authenticated_user_cannot_update_bucketlist_that_doesnt_exist(self):
        rv = self.app.put('/bucketlists/'+ str(200), data=json.dumps(dict(newname='Work')),headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist doesnt exist')

    def test_unauthenticated_user_cannot_update_bucketlist(self):
        bucketlist = Bucketlist(name='Career')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.put('/bucketlists/'+ str(bucketlistID), data=json.dumps(dict(newname='Work')),headers=dict(Authorization=None))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_update_bucketlist_without_token(self):
        bucketlist = Bucketlist(name='Career')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.put('/bucketlists/'+ str(bucketlistID), data=json.dumps(dict(newname='Work')))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')

    def test_user_can_delete_bucketlist(self):
        bucketlist = Bucketlist(name='Visit')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.delete('/bucketlists/'+ str(bucketlistID), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist deleted successfully')

    def test_user_cannot_delete_bucketlist_that_doesnt_exist(self):
        rv = self.app.delete('/bucketlists/'+ str(100), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist doesnt exist')

    def test_unauthenticated_user_cannot_delete_bucketlist(self):
        bucketlist = Bucketlist(name='Visit')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.delete('/bucketlists/'+ str(bucketlistID), headers=dict(Authorization=None))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_delete_bucketlist_without_token(self):
        bucketlist = Bucketlist(name='Visit')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.delete('/bucketlists/'+ str(bucketlistID))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')

    def test_authenticated_user_can_add_item_to_bucketlist(self):
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.post('/bucketlists/' + str(bucketlistID)+ '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        #print(data['message'])
        self.assertEqual(data['message'], 'Bucketlist item added successfully')

    def test_authenticated_user_cannot_add_item_to_bucketlist_that_doesnt_exist(self):
        rv = self.app.post('/bucketlists/' + str(100) + '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        #print(data['message'])
        self.assertEqual(data['message'], 'Bucketlist doesnt exist')

    def test_unauthenticated_user_cannot_add_item_to_bucketlist(self):
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.post('/bucketlists/' + str(bucketlistID) + '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=None))
        data = json.loads(rv.data.decode())
        #print(data['message'])
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_add_item_to_bucketlist_without_token(self):
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.post('/bucketlists/' + str(bucketlistID) + '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )))
        data = json.loads(rv.data.decode())
        #print(data['message'])
        self.assertEqual(data['message'], 'Token not found, Login to get one')

    def test_user_can_update_item_in_bucketlist(self):
        self.app.post('/bucketlists/' + str(self.bucketlistID) + '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        rv = self.app.put('/bucketlists/' + str(self.bucketlistID) + '/items/1', data=json.dumps(dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item updated successfully')

    def test_user_cannot_update_item_in_bucketlist_that_doesnt_exist(self):
        self.app.post('/bucketlists/' + str(self.bucketlistID) + '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        rv = self.app.put('/bucketlists/' + str(100) + '/items/1', data=json.dumps(dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item doesnt exist')

    def test_unauthenticated_user_cannot_update_item_in_bucketlist(self):
        self.app.post('/bucketlists/' + str(self.bucketlistID) + '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        rv = self.app.put('/bucketlists/' + str(self.bucketlistID) + '/items/1', data=json.dumps(dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=None))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_update_item_in_bucketlist_without_token(self):
        self.app.post('/bucketlists/' + str(self.bucketlistID) + '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        rv = self.app.put('/bucketlists/' + str(self.bucketlistID) + '/items/1', data=json.dumps(dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')

    def test_user_can_delete_item_in_bucketlist(self):
        self.app.post('/bucketlists/' + str(self.bucketlistID) + '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        rv = self.app.delete('/bucketlists/' + str(self.bucketlistID) + '/items/1', headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item deleted successfully')

    def test_user_cannot_delete_item_in_bucketlist_that_doesnt_exist(self):
        self.app.post('/bucketlists/' + str(self.bucketlistID) + '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        rv = self.app.put('/bucketlists/' + str(100) + '/items/1', data=json.dumps(dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item doesnt exist')

    def test_unauthenticated_user_cannot_delete_item_in_bucketlist(self):
        self.app.post('/bucketlists/' + str(self.bucketlistID) + '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        rv = self.app.delete('/bucketlists/' + str(self.bucketlistID) + '/items/1', headers=dict(Authorization=None))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_delete_item_in_bucketlist_without_token(self):
        self.app.post('/bucketlists/' + str(self.bucketlistID) + '/items/', data=json.dumps(dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        )), headers=dict(Authorization=self.auth_token))
        rv = self.app.delete('/bucketlists/' + str(self.bucketlistID) + '/items/1')
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')

if __name__ == '__main__':
    unittest.main()