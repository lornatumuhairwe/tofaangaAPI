from .test_base import TestBase
import json, flask
from my_app.product.models import User, Bucketlist
from my_app import db, app, bcrypt


class TestBucketlistModel(TestBase):
    def create_bucketlist(self, bucketlist_name, token):
        return self.app.post('/api/v1/bucketlists/', data=dict(
            name=bucketlist_name), headers=dict(Authorization=token))

    def test_user_can_add_bucketlist(self):
        rv = self.create_bucketlist('Oceans', self.auth_token)
        data = json.loads(rv.data.decode())
        self.assertEqual('Oceans', data['bucketlist'])

    def test_user_cannot_add_bucketlist_without_name(self):
        rv = self.create_bucketlist('', self.auth_token)
        data = json.loads(rv.data.decode())
        self.assertEqual('Bucketlist item should have name', data['message'])

    def test_user_cannot_add_already_existing_bucketlist(self):
        rv = self.create_bucketlist('Cities', self.auth_token)
        data = json.loads(rv.data.decode())
        self.assertEqual('Bucketlist exists',data['message'])

    def test_unauthenticated_user_cannot_add_bucketlist(self):
        rv = self.create_bucketlist('Cities', None)
        data = json.loads(rv.data.decode())
        self.assertEqual('Invalid token, Login again',data['message'])

    def test_return_error_when_token_is_not_found(self):
        rv = self.app.post('/api/v1/bucketlists/', data=dict(name='Work'), headers=dict())
        data = json.loads(rv.data.decode())
        self.assertEqual('Token not found, Login to get one',data['message'])

    def view_all_bucketlists(self, token):
        return self.app.get('/api/v1/bucketlists/', headers=dict(
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
        rv = c.get('/api/v1/bucketlists/?q=Cities')
        assert flask.request.args['q'] == 'Cities'
        assert flask.request.path == '/api/v1/bucketlists/'

    def test_pagination(self):
        rv = self.app.get('/api/v1/bucketlists/?limit=2', headers=dict(
            Authorization=self.auth_token
        ))
        data = json.loads(rv.data.decode())
        self.assertEqual(1, len(data))

    def test_search_and_pagination_of_bucketlist(self):
        self.create_bucketlist('Oceans', self.auth_token)
        self.create_bucketlist('Oceania', self.auth_token)
        self.create_bucketlist('Octopie', self.auth_token)
        rv = self.app.get('/api/v1/bucketlists/?q=Oc&limit=2', headers=dict(
            Authorization=self.auth_token
        ))
        data = json.loads(rv.data.decode())
        self.assertEqual(len(data), 2)
        rv = self.app.get('/api/v1/bucketlists/?q=Zanza&limit=3', headers=dict(
            Authorization=self.auth_token
        ))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'No result matches this search')

    def test_name_based_search_of_bucketlist(self):
        rv = self.app.get('/api/v1/bucketlists/?q=Cities', headers=dict(
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
        rv = self.app.put('/api/v1/bucketlists/'+ str(bucketlistID), data=json.dumps(dict(newname='Work')),
                          headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist updated successfully')

    def test_authenticated_user_cannot_update_bucketlist_that_doesnt_exist(self):
        rv = self.app.put('/api/v1/bucketlists/'+ str(200), data=json.dumps(dict(newname='Work')),
                          headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist doesnt exist')

    def test_unauthenticated_user_cannot_update_bucketlist(self):
        bucketlist = Bucketlist(name='Career')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.put('/api/v1/bucketlists/'+ str(bucketlistID), data=json.dumps(dict(newname='Work')),
                          headers=dict(Authorization=None))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_update_bucketlist_without_token(self):
        bucketlist = Bucketlist(name='Career')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.put('/api/v1/bucketlists/'+ str(bucketlistID), data=json.dumps(dict(newname='Work')))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')

    def test_user_can_delete_bucketlist(self):
        bucketlist = Bucketlist(name='Visit')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.delete('/api/v1/bucketlists/'+ str(bucketlistID), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist deleted successfully')

    def test_user_cannot_delete_bucketlist_that_doesnt_exist(self):
        rv = self.app.delete('/api/v1/bucketlists/'+ str(100), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist doesnt exist')

    def test_unauthenticated_user_cannot_delete_bucketlist(self):
        bucketlist = Bucketlist(name='Visit')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.delete('/api/v1/bucketlists/'+ str(bucketlistID), headers=dict(Authorization=None))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_delete_bucketlist_without_token(self):
        bucketlist = Bucketlist(name='Visit')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.delete('/api/v1/bucketlists/'+ str(bucketlistID))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')