from __future__ import absolute_import

from celery import Celery

#TODO put these in a configuration file
celery = Celery(broker = 'redis://localhost:6379/0',
				backend = 'redis://localhost:6379/0',
				include = ['kickbacker.celery.tasks']
				)


