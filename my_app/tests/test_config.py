import unittest
from my_app import app


class TestDevConfig(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.DevelopmentConfigs')
        return app

    def test_app_in_development(self):
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://localhost/Tofaanga')
        self.assertTrue(app.config['SECRET_KEY'] == 'I love Flask')  # replace is with ==, test is wierd


class TestTestingConfig(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfigs')
        return app

    def test_app_in_testing(self):
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://localhost/TofaangaTest')
        self.assertTrue(app.config['SECRET_KEY'] == 'I love Flask')  # replace is with ==, test is wierd


class TestProductionConfig(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.ProductionConfigs')
        return app

    def test_app_in_testing(self):
        self.assertFalse(app.config['DEBUG'])

if __name__ == '__main__':
    unittest.main()