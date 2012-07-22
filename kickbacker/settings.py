# Here lie the settings

class Config(object):
	DEBUG=False
	HOST='0.0.0.0'
	REDIS_HOST='localhost'
	LOGFILE='/var/log/kickbacker.log'

class ProdConfig(Config):
	DEBUG=False

# Run Server in Debug Mode
class DevConfig(Config):
	DEBUG=True
