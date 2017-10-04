from .test_base import TestBase
import json
from my_app.product.models import Bucketlist
from my_app import db


class TestBucketlistModel(TestBase):

    """ unit tests for bucketlist operations """

    def create_bucketlist(self, bucketlist_name, token):
        """Fuction to test create bucketlist endpoint """
        return self.app.post('/api/v1/bucketlists/', data=dict(
            name=bucketlist_name), headers=dict(Authorization=token))

    def test_user_can_add_bucketlist(self):
        """Ensure that a buckelist can be created given when user is authenticated """
        return_value = self.create_bucketlist('Oceans', self.auth_token)
        data = json.loads(return_value.data.decode())
        self.assertEqual('Oceans', data['bucketlist'])

    def test_user_cannot_add_bucketlist_without_name(self):
        """Ensure that create bucketlist is unsuccessful if bucketlist name is not supplied is given"""
        return_value = self.create_bucketlist('', self.auth_token)
        data = json.loads(return_value.data.decode())
        self.assertEqual('Bucketlist item should have name', data['message'])

    def test_user_cannot_add_already_existing_bucketlist(self):
        """Ensure that create bucketlist is unsuccessful if bucketlist name already exists"""
        return_value = self.create_bucketlist('Cities', self.auth_token)
        data = json.loads(return_value.data.decode())
        self.assertEqual('Bucketlist exists',data['message'])

    def test_unauthenticated_user_cannot_add_bucketlist(self):
        """Ensure that create bucketlist is unsuccessful if user is not authenticated"""
        return_value = self.create_bucketlist('Cities', None)
        data = json.loads(return_value.data.decode())
        self.assertEqual('Invalid token, Login again',data['message'])

    def test_return_error_when_token_is_not_found(self):
        """Ensure that create bucketlist is unsuccessful if no token is supplied"""
        return_value = self.app.post('/api/v1/bucketlists/', data=dict(name='Work'), headers=dict())
        data = json.loads(return_value.data.decode())
        self.assertEqual('Token not found, Login to get one',data['message'])

    def view_all_bucketlists(self, token):
        """Function to test view bucketlist endpoint"""
        return self.app.get('/api/v1/bucketlists/', headers=dict(
            Authorization=token
        ))

    def test_user_can_view_bucketlists(self):
        """Ensure that bucketlist can be viewed if user is authenticated"""
        return_value = self.view_all_bucketlists(self.auth_token)
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['bucketlists']['1'], 'Cities')

    def test_unauthenticated_user_cannot_view_bucketlist(self):
        """Ensure that bucketlist cannot be viewed if user is not authenticated"""
        return_value = self.view_all_bucketlists(None)
        data = json.loads(return_value.data.decode())
        self.assertEqual('Invalid token, Login again',data['message'])

    def test_pagination(self):
        """Ensure that the number bucketlists viewed correspond to pagination"""
        return_value = self.app.get('/api/v1/bucketlists/?limit=2', headers=dict(
            Authorization=self.auth_token
        ))
        data = json.loads(return_value.data.decode())
        self.assertEqual(1, len(data['bucketlists']))

    def test_search_and_pagination_of_bucketlist(self):
        """Ensure that the bucketlist viewed correspond to pagination or/and search"""
        self.create_bucketlist('Oceans', self.auth_token)
        self.create_bucketlist('Oceania', self.auth_token)
        self.create_bucketlist('Octopie', self.auth_token)
        # test for search and pagination when authentication is supplied
        return_value = self.app.get('/api/v1/bucketlists/?q=Oc&limit=2', headers=dict(
            Authorization=self.auth_token
        ))
        data = json.loads(return_value.data.decode())
        self.assertEqual(len(data), 2)
        # test for search and pagination when authentication is supplied and wrong search is provided
        return_value = self.app.get('/api/v1/bucketlists/?q=Zanza&limit=3', headers=dict(
            Authorization=self.auth_token
        ))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Bucketlist not found')
        # test for search when authentication is supplied and wrong search is provided
        return_value = self.app.get('/api/v1/bucketlists/?q=Zanza', headers=dict(
            Authorization=self.auth_token
        ))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Bucketlist not found')

    def test_name_based_search_of_bucketlist(self):
        """Ensure that the number bucketlists viewed correspond to search"""
        return_value = self.app.get('/api/v1/bucketlists/?q=Cities', headers=dict(
            Authorization=self.auth_token
        ))
        data = json.loads(return_value.data.decode())
        self.assertTrue(data['bucketlists'])

    def test_authenticated_user_can_update_bucketlist(self):
        """Ensure that authenticated user can update bucketlist"""
        bucketlist = Bucketlist(name='Career')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        return_value = self.app.put('/api/v1/bucketlists/'+ str(bucketlistID), data=json.dumps(dict(newname='Work')),
                          headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Bucketlist updated successfully')

    def test_authenticated_user_cannot_update_bucketlist_that_doesnt_exist(self):
        """Ensure that user can't update bucketlist that doesnt exist"""
        return_value = self.app.put('/api/v1/bucketlists/'+ str(200), data=json.dumps(dict(newname='Work')),
                          headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Bucketlist doesnt exist')

    def test_unauthenticated_user_cannot_update_bucketlist(self):
        """Ensure that authenticated user can update bucketlist: Invalid token"""
        bucketlist = Bucketlist(name='Career')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        return_value = self.app.put('/api/v1/bucketlists/'+ str(bucketlistID), data=json.dumps(dict(newname='Work')),
                          headers=dict(Authorization=None))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_update_bucketlist_without_token(self):
        """Ensure that authenticated user can update bucketlist: No token supplied"""
        bucketlist = Bucketlist(name='Career')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        return_value = self.app.put('/api/v1/bucketlists/'+ str(bucketlistID), data=json.dumps(dict(newname='Work')))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')

    def test_user_can_delete_bucketlist(self):
        """Ensure that authenticated user can delete bucketlist"""
        bucketlist = Bucketlist(name='Visit')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        return_value = self.app.delete('/api/v1/bucketlists/'+ str(bucketlistID), headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Bucketlist deleted successfully')

    def test_user_cannot_delete_bucketlist_that_doesnt_exist(self):
        """Ensure that authenticated user can't dekete bucketlist that doesn't exist"""
        return_value = self.app.delete('/api/v1/bucketlists/'+ str(100), headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Bucketlist doesnt exist')

    def test_unauthenticated_user_cannot_delete_bucketlist(self):
        """Ensure that unauthenticated user can't delete bucketlist: Invalid token"""
        bucketlist = Bucketlist(name='Visit')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        return_value = self.app.delete('/api/v1/bucketlists/'+ str(bucketlistID), headers=dict(Authorization=None))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_delete_bucketlist_without_token(self):
        """Ensure that unauthenticated user can't delete bucketlist: No token supplied"""
        bucketlist = Bucketlist(name='Visit')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        return_value = self.app.delete('/api/v1/bucketlists/'+ str(bucketlistID))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')
