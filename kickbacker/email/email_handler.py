import logging
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from kickbacker.email import ems

class KickHandler(logging.Handler):
	"""This class logs the error messages"""
	
	def __init__(self):
		print 'hi'
		self.level = logging.ERROR
		self.handle = self
		self.formatter = None

	def setFormatter(self, formatter):
		self.formatter = formatter

	def setLevel(self, level):
		self.level = level

	
	def __call__(self, log_record):
		

		print "Emailing"
		msg = MIMEMultipart('alternative')

		msg['Subject'] = "Kickbacker Server Error"
		msg['From']    = ems.ERROR_EMAIL_FROM
		msg['To']      = ems.ERROR_EMAIL_TO


		text = self.formatter.format(log_record)
		part1 = MIMEText(text, 'plain')
		part2 = MIMEText(text, 'html')

		username = ems.SMTP_USER
		password = ems.SMTP_PASS 

		msg.attach(part1)
		msg.attach(part2)

		s = smtplib.SMTP(ems.SMTP_HOST, ems.SMTP_PORT )

		s.login(username, password)
		s.sendmail(msg['From'], msg['To'], msg.as_string())

		s.quit()
