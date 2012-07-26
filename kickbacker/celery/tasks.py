from __future__ import absolute_import

from kickbacker import kickstarter
from kickbacker.celery.celery_queue import celery


@celery.task
def harvest_project(url):
	kickstarter.get_project(url)

@celery.task
def harvest_backer(url):
	kickstarter.get_backer(url)



