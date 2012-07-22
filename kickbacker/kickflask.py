import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
import redis

class KickFlask(Flask):

	def setup_logging(self):
		# Set logging
		log_filename = self.config['LOGFILE']
		file_handler = RotatingFileHandler(log_filename)
		file_handler.setLevel(logging.INFO)
		self.logger.addHandler(file_handler)

	def connect_redis(self):
		try:
			self.rs = redis.Redis(self.config['REDIS_HOST'])
			self.logger.info("Connected to Redis at %s %s" % (self.config['REDIS_HOST'], self.rs) )
		except Exception as e:
			self.logger.error("Failed to connect to Redis at %s: %s:%s" % (self.config['REDIS_HOST'], e[0], e[1]) )


