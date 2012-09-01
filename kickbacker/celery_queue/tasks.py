from __future__ import absolute_import

from kickbacker import kickstarter
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
	def harvest_backer(url, backer_type):
		kickstarter.get_backer(url, backer_type)



