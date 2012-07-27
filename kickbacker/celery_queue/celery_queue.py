from __future__ import absolute_import

from celery import Celery

from kickbacker import app

#TODO put these in a configuration file
celery = Celery(broker = app.config['CELERY_BROKER'],
				backend = app.config['CELERY_BACKEND'],
				include = app.config['CELERY_INCLUDES'],
				)
