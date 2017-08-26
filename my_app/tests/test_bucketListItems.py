from .test_base import TestBase
import json
from my_app.product.models import Bucketlist
from my_app import db


class TestBucketlistItemMView(TestBase):

    """Unit tests for bucketlist items"""

    def test_authenticated_user_can_add_item_to_bucketlist(self):
        """Ensure that authenticated user can add item to bucketlist"""
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        return_value = self.app.post('/api/v1/bucketlists/' + str(bucketlistID)+ '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item added successfully')

    def test_authenticated_user_cannot_add_item_to_bucketlist_that_doesnt_exist(self):
        """Ensure that user can't add item to bucketlist that doesn't exist"""
        return_value = self.app.post('/api/v1/bucketlists/' + str(100) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        # print(data['message'])
        self.assertEqual(data['message'], "Bucketlist doesn't exist")

    def test_unauthenticated_user_cannot_add_item_to_bucketlist(self):
        """Ensure that unauthenticated user can't add item to bucketlist: invalid token"""
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        return_value = self.app.post('/api/v1/bucketlists/' + str(bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=None))
        data = json.loads(return_value.data.decode())
        # print(data['message'])
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_add_item_to_bucketlist_without_token(self):
        """Ensure that unauthenticated user can't add item to bucketlist: no token supplied"""
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        return_value = self.app.post('/api/v1/bucketlists/' + str(bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ))
        data = json.loads(return_value.data.decode())
        # print(data['message'])
        self.assertEqual(data['message'], 'Token not found, Login to get one')

    def test_authenticated_user_can_get_item_in_bucketlist(self):
        """Ensure that authenticated user can get items in bucketlist"""
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id

        return_value = self.app.get('/api/v1/bucketlists/' + str(bucketlistID), headers=dict(Authorization=self.auth_token))
        data1 = json.loads(return_value.data.decode())
        self.assertEqual(data1['message'], 'No items in this bucketlist')
        self.app.post('/api/v1/bucketlists/' + str(bucketlistID)+ '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        return_value = self.app.get('/api/v1/bucketlists/' + str(bucketlistID), headers=dict(Authorization=self.auth_token))
        data2 = json.loads(return_value.data.decode())
        self.assertEqual(data2['1'], 'Indian Ocean')

    def test_authenticated_user_can_get_search_and_paginate_items_in_bucketlist(self):
        """Ensure that items displayed correspond to search and pagination"""
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        # test pagination of items from existing bucketlist
        return_value = self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?limit=2',
                           headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'No items in this bucketlist')
        self.app.post('/api/v1/bucketlists/' + str(bucketlistID)+ '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        self.app.post('/api/v1/bucketlists/' + str(bucketlistID) + '/items/', data=dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        self.app.post('/api/v1/bucketlists/' + str(bucketlistID) + '/items/', data=dict(
            title='Atlantic Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        # test search of items from existing bucketlist
        return_value = self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?q=Ocean',
                           headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(len(data), 3)
        # test pagination of items from existing bucketlist
        return_value = self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?limit=2',
                           headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(len(data), 2)
        # test getting of items from existing bucketlist with invalid auth key
        return_value = self.app.get('/api/v1/bucketlists/' + str(bucketlistID),
                           headers=dict(Authorization=None))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], "Invalid token, Login again")
        # test getting of items from existing bucketlist without auth key supplied
        return_value = self.app.get('/api/v1/bucketlists/' + str(bucketlistID))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], "Token not found, Login to get one")
        # test getting of items from bucketlist that doesn't exist
        return_value = self.app.get('/api/v1/bucketlists/' + '100',
                           headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], "Bucketlist doesnt exist")
        # test pagination of items from bucketlist that doesn't exist
        return_value = self.app.get('/api/v1/bucketlists/' + '100' + '?limit=2',
                           headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], "Bucketlist doesn't exist")
        # test searching of items from bucketlist that doesn't exist
        return_value = self.app.get('/api/v1/bucketlists/' + '100' + '?q=Zanza',
                           headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], "Bucketlist doesnt exist")
        # test getting non existing items from bucketlist
        return_value = self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?q=Zanzi',
                           headers=dict(Authorization=self.auth_token))
        data2 = json.loads(return_value.data.decode())
        self.assertEqual(data2['message'], 'Bucketlist not found')
        # test pagination and search of items from bucketlist
        return_value = self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?q=Ocean&limit=2',
                           headers=dict(Authorization=self.auth_token))
        data3 = json.loads(return_value.data.decode())
        self.assertEqual(len(data3), 2)
        # test search of items from bucketlist that don't exist
        return_value = self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?q=Zanzi&limit=2',
                           headers=dict(Authorization=self.auth_token))
        data4 = json.loads(return_value.data.decode())
        self.assertEqual(data4['message'], 'No result matches this search')

    def test_user_can_update_item_in_bucketlist(self):
        """Ensure that user can update bucketlist items"""
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        return_value = self.app.put('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1', data=dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item updated successfully')

    def test_user_cannot_update_item_in_bucketlist_that_doesnt_exist(self):
        """Ensure that user cannot update non existent bucketlist items"""
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        return_value = self.app.put('/api/v1/bucketlists/' + str(100) + '/items/1', data=dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item doesnt exist')

    def test_unauthenticated_user_cannot_update_item_in_bucketlist(self):
        """Ensure that authorized user can't update bucketlist items"""
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        return_value = self.app.put('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1', data=dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=None))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_update_item_in_bucketlist_without_token(self):
        """Ensure that authorized user can't update bucketlist items: No token supplied"""
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        return_value = self.app.put('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1', data=dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')

    def test_user_can_delete_item_in_bucketlist(self):
        """Ensure that user can delete bucketlist items"""
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        return_value = self.app.delete('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1',
                             headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item deleted successfully')

    def test_user_cannot_delete_item_in_bucketlist_that_doesnt_exist(self):
        """Ensure that user can't delete bucketlist items that dont exist"""
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        return_value = self.app.put('/api/v1/bucketlists/' + str(100) + '/items/1', data=dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item doesnt exist')

    def test_unauthenticated_user_cannot_delete_item_in_bucketlist(self):
        """Ensure that unauthenticated user can't delete bucketlist items: Invalid token"""
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        return_value = self.app.delete('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1',
                             headers=dict(Authorization=None))
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_delete_item_in_bucketlist_without_token(self):
        """Ensure that unauthenticated user can't delete bucketlist items: Invalid token"""
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        return_value = self.app.delete('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1')
        data = json.loads(return_value.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')
