
class DevelopmentConfigs:
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'postgresql://lorna:enambi@localhost/Tofaanga'
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/Tofaanga'
    SECRET_KEY = 'I love Flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class TestingConfigs:
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'postgresql://lorna:enambi@localhost/TofaangaTest'
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/TofaangaTest'
    SECRET_KEY = 'I love Flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class ProductionConfigs:
    DEBUG = False
    # SQLALCHEMY_DATABASE_URI = 'postgresql://lorna:enambi@localhost/TofaangaTest'
    # SECRET_KEY = 'I love Flask'
    # SQLALCHEMY_TRACK_MODIFICATIONS = True