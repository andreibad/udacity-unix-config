#!/user/bin/python

import sys

sys.path.insert(0, '/var/www/')

from catalog import app as application

application.secret_key = 'xxx123'
