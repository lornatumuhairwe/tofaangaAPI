import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from my_app import app, db
app.config.from_object('config.DevelopmentConfigs')
app.config.from_object('configTest')


migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

