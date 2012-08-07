import os

# Here lie the settings

class Config(object):
	HOME = os.path.abspath(os.path.dirname(__file__)) + '/'
	DEBUG = False
	HOST = '0.0.0.0'
	PORT = 8000
	LOGFILE = '/var/log/kickbacker.log'
	REDIS_HOST = 'localhost'
	REDIS_PORT = '6379'
	REDIS_DB = 0
	CELERY_BROKER = 'redis://%s:%s/%s' % (REDIS_HOST, REDIS_PORT, REDIS_DB)
	CELERY_BACKEND = 'redis://%s:%s/%s' % (REDIS_HOST, REDIS_PORT, REDIS_DB)
	CELERY_INCLUDES = ['kickbacker.celery_queue.tasks']


class ProdConfig(Config):
	DEBUG=False

# Run Server in Debug Mode
class DevConfig(Config):
	DEBUG=True