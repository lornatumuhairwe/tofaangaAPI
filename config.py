
class DevelopmentConfigs:
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'postgresql://lorna:enambi@localhost/Tofaanga'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/Tofaanga'
    #SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/TofaangaTest'
    SQLALCHEMY_DATABASE_URI = 'postgres://ywppqdxpacdety:c557ee67fc1c9a4276d9546c617ffda2f79b313a0e4b6f1fb1fed5567941370f@ec2-107-22-223-6.compute-1.amazonaws.com:5432/d3aup0re5faojo'
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