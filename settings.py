import os
import secrets

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
	SMTP_HOST = 'smtp.mandrillapp.com'
	SMTP_PORT = '587'
	SMTP_USER = 'jsh2134+kickbacker@gmail.com'
	SMTP_PASS = secrets.MANDRILL_SMTP
	ERROR_EMAIL_TO = 'jsh2134+kball@gmail.com'
	ERROR_EMAIL_FROM = 'kickserver@kickbacker.co'


class ProdConfig(Config):
	DEBUG=False
	KB_BASE_SHORT = 'http://awe.sm/'
	KB_BASE = 'http://kickbacker.co/'

# Run Server in Debug Mode
class DevConfig(Config):
	DEBUG=True
	KB_BASE_SHORT = 'http://demo.awe.sm/'
	KB_BASE = 'http://localhost:5000/'
