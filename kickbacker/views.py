# -*- coding: utf-8 -*-
import datetime

from flask import render_template
from flask import request
from flask import jsonify
from flask import redirect
from flask import make_response

from kickbacker import app
from kickbacker import lib
from kickbacker import datalib
from kickbacker import kickstarter
from kickbacker.celery_queue import tasks

def make_timestamp(time_str, time_format="%Y-%m-%d %H:%M:%S.%f"):
	return datetime.datetime.strptime(time_str, time_format)


def respond_index(project_id):
	project = datalib.get_project(app.rs, project_id)
	return render_template('get_project.html', project=project)


def show_backer(backer):
	backer_dict = datalib.get_backer(app.rs, backer)
	return render_template('show_backer.html', 
								backer = backer_dict )


def show_backers(project_id):
	backers = {}
	backer_list = datalib.get_project_backers(app.rs, project_id)
	for backer in backer_list:
		backers[backer] = datalib.get_backer(app.rs, backer)

	project = datalib.get_project(app.rs, project_id)

	return render_template('show_backers.html', 
								backer_list = backers,
								project = project )

def show_projects():
	projects = {}
	project_list = datalib.get_projects(app.rs)
	for project_id in project_list:
		projects[project_id] = datalib.get_project(app.rs, project_id)
	return render_template('show_projects.html',
								projects = projects)

def get_project_backers():
	project_url = request.form.get('url')
	project_id, project_backers = kickstarter.get_backers(app.rs, project_url)
	if project_id:
		return jsonify({'id':project_id, 'backers':project_backers})

def key_redirect(project_id, backer_id):
	""" Lookups proper redirect, logs clicks, sets cookie """
	raw_key = request.values.get('awesm')
	key = raw_key.split('_')[1]
	redirect_url = datalib.get_redirect(app.rs, key)
	app.logger.info("Redirecting to %s" % (redirect_url) )

	# Increment Clicks
	datalib.increment_short_key_value(app.rs, key, 'clicks')
	datalib.increment_backer_value(app.rs, backer_id, 'clicks')
	datalib.increment_project_value(app.rs, project_id, 'clicks')

	# Store Referral URL (for now)
	datalib.add_short_key_referrer(app.rs, key, request.referrer)

	# Set Redirect URL
	resp = make_response( redirect(redirect_url) )

	# Set cookie with the project and backer ids
	resp.set_cookie('kb_%s_%s' % (backer_id, project_id),
					'%s:%s' % (backer_id, project_id),
					max_age=231000000)

	return resp


def add_short_key():
	key = request.form.get('key')
	url = request.form.get('url')
	kb_url = request.form.get('kb_url')
	backer_id = request.form.get('backer_id')
	project_id = request.form.get('project_id')
	
	url = lib.strip_url_args(url)

	create_new_project(backer_id, project_id, key, kb_url, url)

	return jsonify( {   'success':True, 
						'message':'Added key:%s for backer:%s to project:%s' \
									% (key, backer_id, project_id)})


def create_new_project(backer_id, project_id, key, kb_url, url):

	# Queue up backer scrape job
	datalib.add_backer(app.rs, backer_id)
	tasks.harvest_backer.delay(kickstarter.BACKER_URL % (backer_id))

	# Queue up project scrape job
	datalib.add_project(app.rs, project_id)
	tasks.harvest_project.delay(url)

	datalib.add_project_backer(app.rs, project_id, backer_id)
	datalib.add_short_key(app.rs, key)
	datalib.add_backer_short_key(app.rs, backer_id, key)
	datalib.add_project_short_key(app.rs, project_id, key)
	datalib.add_redirect(app.rs, key, url)
	datalib.update_short_key(app.rs, key, 'clicks', 0)
	datalib.update_short_key(app.rs, key, 'url', url)
	datalib.update_short_key(app.rs, key, 'created', datetime.datetime.now())
	datalib.update_short_key(app.rs, key, 'project_id', project_id)
	datalib.update_short_key(app.rs, key, 'backer_id', backer_id)


def dashboard():
	""" Display stats about all projects"""	
	project_dict={}
	projects = datalib.get_projects(app.rs)
	total_clicks = 0
	for project_id in projects:
		project_dict[project_id] = datalib.get_project(app.rs, project_id)

		if 'clicks' in project_dict[project_id]:
			total_clicks += int(project_dict[project_id]['clicks'])

		project_dict[project_id]['backers'] = \
					datalib.get_project_backers(app.rs, project_id)
		project_dict[project_id]['key_set'] = \
					datalib.get_project_short_keys(app.rs, project_id)

		project_dict[project_id]['keys'] = {}
		for key in project_dict[project_id]['key_set']:
			project_dict[project_id]['keys'][key] = \
								datalib.get_short_key(app.rs, key)

			# Format Timestamp
			project_dict[project_id]['keys'][key]['created'] = \
							make_timestamp(project_dict[project_id]['keys'][key]['created'])

			project_dict[project_id]['keys'][key]['referrers'] = \
							datalib.get_short_key_referrer_list(app.rs, key)
		
	return render_template('show_dashboard.html',
								projects = project_dict,
								total_clicks = total_clicks)

def leaderboard(project_id):
	""" Display project stats """
	project = datalib.get_project(app.rs, project_id)

	if not project:
		return render_template('not_found.html', \
										nf_type = "project",
										nf_id = project_id)
	else:
		project_backers = datalib.get_project_backers(app.rs, project_id)
		project_keys = datalib.get_project_short_keys(app.rs, project_id)

		total_clicks = 0
		backer_dict = {}
		for backer_id in project_backers:
			backer_dict[backer_id] = datalib.get_backer(app.rs, backer_id)
			backer_key_list = datalib.get_backer_short_keys(app.rs, backer_id)
			for key_id in backer_key_list:
				if key_id in project_keys:
					backer_dict[backer_id]['key'] = datalib.get_short_key(app.rs, key_id)
					backer_dict[backer_id]['key']['id'] = datalib.get_short_key(app.rs, key_id)
					backer_dict[backer_id]['key']['badges'] = 0

					# Aggregate Clicks
					total_clicks += int(backer_dict[backer_id]['key']['clicks'])
					
					# Format Timestamp
					backer_dict[backer_id]['key']['created'] = \
										make_timestamp(backer_dict[backer_id]['key']['created'])

		sorted_backers = backer_dict.keys()
		sorted_backers.sort(lambda x,y: cmp(
								int(backer_dict[y]['key']['clicks']), 
								int(backer_dict[x]['key']['clicks'])
								)
							)
		return render_template('show_leaderboard.html',
									project = project,
									backers = backer_dict,
									sorted_backers = sorted_backers,
									total_clicks = total_clicks)
