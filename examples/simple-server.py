#!/usr/bin/env python
import json

from flask.ext.script import Manager
from bdfu.webapp import app

def configure_app(config):
    with open(config, 'r') as f:
        config_dict = json.load(f)
    app.config['JWT_SECRET_KEY'] = config_dict['secret']
    app.config['STORAGE_DIR'] = config_dict['storage']
    return app

manager = Manager(configure_app)
manager.add_option(
    '-c', '--config', dest='config',
    help='JSON file to load configuration from',
    required=True,
)

if __name__ == '__main__':
    manager.run()

