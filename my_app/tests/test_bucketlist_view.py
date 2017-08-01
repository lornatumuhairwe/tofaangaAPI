# import json
# from my_app import db, app
# from my_app.product.models import User
# import unittest
#
# class TestBucketlistModel(unittest.TestCase):
#     def setUp(self):
#         app.config.from_object('config.TestingConfigs')
#         db.session.close()
#         db.drop_all()
#         db.create_all()
#         user = User('testi', 'testpass')
#         db.session.add(user)
#         db.session.commit()
#         self.app = app.test_client()
#         return self.app