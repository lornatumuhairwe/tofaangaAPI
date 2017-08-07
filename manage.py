from unittest import TestLoader, TextTestRunner
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from my_app import app, db
from coverage import Coverage
app.config.from_object('config.DevelopmentConfigs')
app.config.from_object('config.TestingConfigs')

cov = Coverage(
    branch=True,
    include='my_app/*',
    omit=[
        'my_app/tests/*',
        'venv/*',
        'my_app/__init__.py',
        'my_app/product/models.py'
    ]
)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def testing():
    if run_tests():
        return 0
    return 1


@manager.command
def test_coverage():
    if run_tests():
        cov.use_cache(True)
        cov.stop()
        cov.save()
        print('Coverage report: ')
        cov.report()
        cov.xml_report()
        return 0
    return 1

def run_tests():
    cov.start()
    tests = TestLoader().discover('my_app.tests', pattern='test*.py')
    return TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()

