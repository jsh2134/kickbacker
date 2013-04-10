import os
import secrets
from kickbacker.email import ems

# Here lie the settings

class Config(object):
	HOME = os.path.abspath(os.path.dirname(__file__)) + '/'
	DEBUG = False
	HOST = '0.0.0.0'
	PORT = 5000
	LOGFILE = '/var/log/kickbacker.log'
	REDIS_HOST = 'localhost'
	REDIS_PORT = '6379'
	REDIS_DB = 0
	CELERY_BROKER = 'redis://%s:%s/%s' % (REDIS_HOST, REDIS_PORT, REDIS_DB)
	CELERY_BACKEND = 'redis://%s:%s/%s' % (REDIS_HOST, REDIS_PORT, REDIS_DB)
	CELERY_INCLUDES = ['kickbacker.celery_queue.tasks']
	SMTP_HOST = ems.SMTP_HOST
	SMTP_PORT = ems.SMTP_PORT 
	SMTP_USER = ems.SMTP_USER 
	SMTP_PASS = ems.SMTP_PASS
	ERROR_EMAIL_TO = ems.ERROR_EMAIL_TO
	ERROR_EMAIL_FROM = ems.ERROR_EMAIL_FROM


class ProdConfig(Config):
	DEBUG=False
	KB_BASE_SHORT = 'http://awe.sm/'
	KB_BASE = 'http://kickbacker.co/'

# Run Server in Debug Mode
class DevConfig(Config):
	DEBUG=True
	KB_BASE_SHORT = 'http://demo.awe.sm/'
	KB_BASE = 'http://localhost:5000/'
