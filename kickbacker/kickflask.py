import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import SMTPHandler

from flask import Flask
import redis

class KickFlask(Flask):

	def setup_logging(self):

		# Logging format
		kb_fmt = u'[%(asctime)s %(levelname)s] - %(processName)s (%(process)s) - (%(module)s:%(funcName)s:%(lineno)s) %(message)s'
		kb_formatter = logging.Formatter(fmt=kb_fmt)

		# File Log
		log_filename = self.config['LOGFILE']
		file_handler = RotatingFileHandler(log_filename)

		if self.config['DEBUG']:
			file_handler.setLevel(logging.INFO)
		else:
			file_handler.setLevel(logging.ERROR)

		file_handler.setFormatter(kb_formatter)
		self.logger.addHandler(file_handler)

		# Email Log
		credentials = [ self.config['SMTP_USER'], self.config['SMTP_PASS'] ]
		host_info = ( self.config['SMTP_HOST'], self.config['SMTP_PORT'] )
		#host_info = self.config['SMTP_HOST']
		mail_handler = SMTPHandler(host_info, \
                                self.config['ERROR_EMAIL_FROM'], \
                                [self.config['ERROR_EMAIL_TO']], \
								'Kickbacker Server Failure',\
								credentials = credentials, secure=() )
		mail_handler.setLevel(logging.ERROR)
		mail_handler.setFormatter(kb_formatter)
		self.logger.addHandler(mail_handler)


	def connect_redis(self):
		try:
			self.rs = redis.Redis(self.config['REDIS_HOST'])
			self.logger.info("Connected to Redis at %s %s" % (self.config['REDIS_HOST'], self.rs) )
		except Exception as e:
			self.logger.error("Failed to connect to Redis at %s: %s:%s" % (self.config['REDIS_HOST'], e[0], e[1]) )


