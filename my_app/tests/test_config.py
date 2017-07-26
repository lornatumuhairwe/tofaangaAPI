#import context
import unittest
from my_app import app


class TestDevConfig(unittest.TestCase):
    def test_app_is_testing(self):
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://lorna:enambi@localhost/Tofaanga')
        self.assertFalse(app.config['SECRET_KEY'] is 'I love Flaskkk') #replace is with ==, test is wierd

if __name__=='__main__':
    unittest.main()