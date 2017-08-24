from .test_base import TestBase
import json
from my_app.product.models import User, Bucketlist
from my_app import db, app, bcrypt


class TestBucketlistItemMView(TestBase):
    def test_authenticated_user_can_add_item_to_bucketlist(self):
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.post('/api/v1/bucketlists/' + str(bucketlistID)+ '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item added successfully')

    def test_authenticated_user_cannot_add_item_to_bucketlist_that_doesnt_exist(self):
        rv = self.app.post('/api/v1/bucketlists/' + str(100) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        # print(data['message'])
        self.assertEqual(data['message'], "Bucketlist doesn't exist")

    def test_unauthenticated_user_cannot_add_item_to_bucketlist(self):
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.post('/api/v1/bucketlists/' + str(bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=None))
        data = json.loads(rv.data.decode())
        # print(data['message'])
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_add_item_to_bucketlist_without_token(self):
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv = self.app.post('/api/v1/bucketlists/' + str(bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ))
        data = json.loads(rv.data.decode())
        # print(data['message'])
        self.assertEqual(data['message'], 'Token not found, Login to get one')

    def test_authenticated_user_can_get_item_in_bucketlist(self):
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id

        rv1 = self.app.get('/api/v1/bucketlists/' + str(bucketlistID), headers=dict(Authorization=self.auth_token))
        data1 = json.loads(rv1.data.decode())
        self.assertEqual(data1['message'], 'No items in this bucketlist')
        self.app.post('/api/v1/bucketlists/' + str(bucketlistID)+ '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        rv2 = self.app.get('/api/v1/bucketlists/' + str(bucketlistID), headers=dict(Authorization=self.auth_token))
        data2 = json.loads(rv2.data.decode())
        self.assertEqual(data2['1'], 'Indian Ocean')

    def test_authenticated_user_can_get_search_and_paginate_items_in_bucketlist(self):
        bucketlist = Bucketlist(name='Water bodies')
        db.session.add(bucketlist)
        self.user.bucketlists.append(bucketlist)  # FK relationship
        db.session.commit()
        bucketlistID = bucketlist.id
        rv1 = self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?limit=2',
                           headers=dict(Authorization=self.auth_token))
        data = json.loads(rv1.data.decode())
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
        rv1= self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?q=Ocean',
                           headers=dict(Authorization=self.auth_token))
        data = json.loads(rv1.data.decode())
        self.assertEqual(len(data), 3)
        rv1 = self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?limit=2',
                           headers=dict(Authorization=self.auth_token))
        data = json.loads(rv1.data.decode())
        self.assertEqual(len(data), 2)
        rv2 = self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?q=Zanzi',
                           headers=dict(Authorization=self.auth_token))
        data2 = json.loads(rv2.data.decode())
        self.assertEqual(data2['message'], 'Bucketlist not found')
        rv3 = self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?q=Ocean&limit=2', headers=dict(Authorization=self.auth_token))
        data3 = json.loads(rv3.data.decode())
        self.assertEqual(len(data3), 2)
        rv2 = self.app.get('/api/v1/bucketlists/' + str(bucketlistID) + '?q=Zanzi&limit=2', headers=dict(Authorization=self.auth_token))
        data4 = json.loads(rv2.data.decode())
        self.assertEqual(data4['message'], 'No result matches this search')

    def test_user_can_update_item_in_bucketlist(self):
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        rv = self.app.put('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1', data=dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item updated successfully')

    def test_user_cannot_update_item_in_bucketlist_that_doesnt_exist(self):
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        rv = self.app.put('/api/v1/bucketlists/' + str(100) + '/items/1', data=dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item doesnt exist')

    def test_unauthenticated_user_cannot_update_item_in_bucketlist(self):
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        rv = self.app.put('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1', data=dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=None))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_update_item_in_bucketlist_without_token(self):
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        rv = self.app.put('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1', data=dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')

    def test_user_can_delete_item_in_bucketlist(self):
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        rv = self.app.delete('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1',
                             headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item deleted successfully')

    def test_user_cannot_delete_item_in_bucketlist_that_doesnt_exist(self):
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        rv = self.app.put('/api/v1/bucketlists/' + str(100) + '/items/1', data=dict(
            title='Pacific Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Bucketlist item doesnt exist')

    def test_unauthenticated_user_cannot_delete_item_in_bucketlist(self):
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        rv = self.app.delete('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1', headers=dict(Authorization=None))
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Invalid token, Login again')

    def test_user_cannot_delete_item_in_bucketlist_without_token(self):
        self.app.post('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/', data=dict(
            title='Indian Ocean',
            deadline='13/11/1994',
            status='Incomplete'
        ), headers=dict(Authorization=self.auth_token))
        rv = self.app.delete('/api/v1/bucketlists/' + str(self.bucketlistID) + '/items/1')
        data = json.loads(rv.data.decode())
        self.assertEqual(data['message'], 'Token not found, Login to get one')
