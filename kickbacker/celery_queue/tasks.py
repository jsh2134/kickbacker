from __future__ import absolute_import

from kickbacker import kickstarter
from kickbacker.email import contact

import logging

try:
	from kickbacker.celery_queue.celery_queue import celery_server
except:
	celery_server = None
	print "Warning Celery is not Running"
	logging.warn("Warning Celery not running")

if celery_server:
	@celery_server.task
	def harvest_project(url):
		kickstarter.get_project(url)

	@celery_server.task
	def harvest_backer(url):
		kickstarter.get_backer(url)

	@celery_server.task
	def welcome_backer(email, kb_type, backer_id, \
									project_id, new_backer):
		contact.send_welcome_mail(email, kb_type, backer_id,
									 project_id, new_backer)
	
