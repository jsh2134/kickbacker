# -*- coding: utf-8 -*-
import datetime
import logging
import urllib
import random

from flask import render_template
from flask import request
from flask import jsonify
from flask import redirect
from flask import make_response

from kickbacker import app
from kickbacker import lib
from kickbacker import datalib
from kickbacker import rewards
from kickbacker import kickstarter
from kickbacker import defaults
from kickbacker.celery_queue import tasks

logging.basicConfig(filename='/var/log/kickbacker.log', level=logging.INFO)

def make_timestamp(time_str, time_format="%Y-%m-%d %H:%M:%S.%f"):
	return datetime.datetime.strptime(time_str, time_format)


def respond_index(project_id):
	project = datalib.get_project(app.rs, project_id)
	# Redirect to backer focused page
	if project_id:
		lead_type = 'backer'
		try:
			project_prize = datalib.get_prize(app.rs, project['backer_prize'])
		except:
			logging.exception('Index: No prize found for project %s' % project)
			project_prize = "No Prize Has been Set"
		project['backer_prize'] = project_prize
	else:
		lead_type = 'owner'
	
	sample_projects = list(datalib.get_projects(app.rs))
	sample_project_id = random.choice(sample_projects)
	sample_board_link = '%s/leaderboard/' % sample_project_id
	return render_template('index.html', project=project,
										 lead_type=lead_type,
										 sample_board=sample_board_link)

def respond_contact():
	return render_template('contact.html')


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


def edit_project(project_id):
	project = datalib.get_project(app.rs, project_id)
	project['id'] = project_id 
	return render_template('edit_project.html', 
	 					project=project,
						)


def save_project(project_id, prize_id):
	a = datalib.update_project(app.rs, project_id, 'backer_prize',  prize_id)
	return jsonify({'success': a})


def get_project_backers():
	project_url = request.form.get('url')
	project_id, project_backers = kickstarter.get_backers(app.rs, project_url)
	if project_id:
		return jsonify({'id':project_id, 'backers':project_backers})


def key_redirect(project_id, backer_id):
	""" Lookups proper redirect, logs clicks, sets cookie """

	# Expensive
	project_keys = set(datalib.get_project_short_keys(app.rs, project_id))
	backer_keys = set(datalib.get_backer_short_keys(app.rs, backer_id))

	key = list(project_keys & backer_keys)[0]
	print 'found key: %s' % key
	redirect_url = datalib.get_redirect(app.rs, key)

	redirect_url = '%s?utm_source=kickbacker&utm_campaign=kickbacker_share' % (redirect_url)

	# TODO if you have cookie don't count
	# Increment Clicks
	datalib.increment_short_key_value(app.rs, key, 'clicks')
	datalib.increment_backer_value(app.rs, backer_id, 'clicks')
	datalib.increment_project_value(app.rs, project_id, 'clicks')

	# Store Referral URL (for now)
	if request.referrer:
		datalib.add_short_key_referrer(app.rs, key, request.referrer)
		rewards.check_for_rewards(key, request.referrer)

	# Set Redirect URL
	resp = make_response( redirect(redirect_url) )

	# Set cookie with the project and backer ids
	resp.set_cookie('kb_%s_%s' % (backer_id, project_id),
					'%s:%s' % (backer_id, project_id),
					max_age=231000000)

	return resp


def new_short_key():
	key = request.form.get('key')
	url = request.form.get('url')
	kb_url = request.form.get('kb_url')
	backer_id = request.form.get('backer_id')
	project_id = request.form.get('project_id')
	email = request.form.get('email')
	kb_type = request.form.get('kb_type')
	awesm_url = urllib.unquote_plus(request.form.get('awesm_url'))

	url = lib.strip_url_args(url)

	create_new_project(backer_id, project_id, key, kb_url, \
						url, email, kb_type, awesm_url)

	return jsonify( {   'success':True, 
						'message':'Added key:%s for backer:%s to project:%s' \
									% (key, backer_id, project_id)})


def show_prizes(project_id):

	prizes_added = datalib.get_project_prizes(app.rs, project_id)
	if prizes_added:
		prizes = {}
		prize_ids = datalib.get_project_prizes(app.rs, project_id)
		for prize_id in prize_ids:
			prizes[prize_id] = datalib.get_prize(app.rs, prize_id)
		
		if prizes:
			sorted_prizes = prizes.keys()
			sorted_prizes.sort(lambda x,y : cmp(
												int(prizes[x]['value']),
												int(prizes[y]['value'])
											))
			pl = []
			for prize in sorted_prizes:
				pl.append( prizes[prize] )
			return jsonify({'success': True, 'prizes' :pl})
		else:
			return jsonify({'success': False, 'message':'No prizes found'})
	else:
		return jsonify({'success': False, 'message':'Prizes not added yet'})


def create_new_project(backer_id, project_id, key, \
						kb_url, url, email, kb_type, awesm_url):

	# Queue up project scrape job
	# will only add project if new project created
	# new kickbackers will use exsting project
	if datalib.add_project(app.rs, project_id):
		# Add Project specific values
		datalib.update_project(app.rs, project_id, 'awesm_url', awesm_url)
		datalib.update_project(app.rs, project_id, 'kb_creator', backer_id)

		tasks.harvest_project.delay(url)

	new_backer = False
	# Queue up backer scrape job
	if datalib.add_backer(app.rs, backer_id):
		tasks.harvest_backer.delay(kickstarter.BACKER_URL % (backer_id))
		new_backer = True

	# Queue up backer welcome email job
	# have: email, kb_type, new_backer
	# need: project info, backer info
	tasks.welcome_backer.delay(email, kb_type, backer_id,\
									 project_id, new_backer)

	# Add KickBacker
	datalib.add_kickbacker(app.rs, email)
	datalib.update_kickbacker(app.rs, email, 'project', project_id)
	datalib.update_kickbacker(app.rs, email, 'backer',  backer_id)
	datalib.update_kickbacker(app.rs, email, 'backer_type',  kb_type)

	datalib.add_project_backer(app.rs, project_id, backer_id)


	# Add Backer specific values
	datalib.update_backer(app.rs, backer_id, 'type', kb_type)
	datalib.update_backer(app.rs, backer_id, 'awesm_url', awesm_url)
	datalib.update_backer(app.rs, backer_id, 'backer_type', kb_type)
	datalib.add_backer_short_key(app.rs, backer_id, key)

	# Add Short Key for the project
	datalib.add_short_key(app.rs, key)
	datalib.add_project_short_key(app.rs, project_id, key)
	datalib.add_redirect(app.rs, key, url)
	datalib.update_short_key(app.rs, key, 'clicks', 1)
	datalib.update_short_key(app.rs, key, 'url', url)
	datalib.update_short_key(app.rs, key, 'created', \
										datetime.datetime.now())
	datalib.update_short_key(app.rs, key, 'project_id', project_id)
	datalib.update_short_key(app.rs, key, 'backer_id', backer_id)
	datalib.update_short_key(app.rs, key, 'backer_type',  kb_type)



def projectboard():
	""" Display stats about all projects"""	
	project_dict={}
	projects = datalib.get_projects(app.rs)
	total_clicks = 0
	for project_id in projects:
		project_dict[project_id] = datalib.get_project(app.rs, project_id)

		if 'clicks' in project_dict[project_id]:
			total_clicks += int(project_dict[project_id]['clicks'])
		else:
			total_clicks = 0


	return render_template('show_projectboard.html',
								projects = project_dict,
								total_clicks = total_clicks)

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

def leaderboard(project_id, share=False, backer_arg=None):
	""" Display project stats """
	project = datalib.get_project(app.rs, project_id)

	if not project:
		return render_template('not_found.html', \
										nf_type = "project",
										nf_id = project_id)
	else:
		try:
			project_prize = datalib.get_prize(app.rs, project['backer_prize'])
		except:
			logging.exception('Leaderboard: No prize found for project %s' % project)
			project_prize = "No Prize Has been Set"

		project['backer_prize'] = project_prize

		project_backers = datalib.get_project_backers(app.rs, project_id)
		project_keys = datalib.get_project_short_keys(app.rs, project_id)

		total_clicks = 0
		max_clicks = 0
		backer_dict = {}
		for backer_id in project_backers:
			backer_info = datalib.get_backer(app.rs, backer_id)
			# Ignore Owners
			if 'backer_type' in backer_info and backer_info['backer_type'] == 'backer':
				backer_dict[backer_id] = backer_info
				backer_key_list = datalib.get_backer_short_keys(app.rs, backer_id)
				for key_id in backer_key_list:
					if key_id in project_keys:
						backer_dict[backer_id]['key'] = datalib.get_short_key(app.rs, key_id)
						backer_dict[backer_id]['key']['id'] = key_id
						backer_dict[backer_id]['key']['rewards'] = datalib.get_rewards(app.rs, key_id)

						# Aggregate Clicks
						total_clicks += int(backer_dict[backer_id]['key']['clicks'])

						if int(backer_dict[backer_id]['key']['clicks']) > max_clicks:
							max_clicks =  int(backer_dict[backer_id]['key']['clicks'])

						# Format Timestamp
						backer_dict[backer_id]['key']['created'] = \
											make_timestamp(backer_dict[backer_id]['key']['created'])

		# Populate with Fake Backers if New Project
		MAX_FAKES = 3
		num_backers = len(backer_dict.keys())
		if num_backers < MAX_FAKES:
			for fake_backer in defaults.FAKE_BACKERS[0:MAX_FAKES-num_backers]:
				fake_backer['key']['clicks'] = random.randint(0,max_clicks-1)
				backer_dict[fake_backer['name']] = fake_backer
				

		sorted_backers = backer_dict.keys()
		sorted_backers.sort(lambda x,y: cmp(
								int(backer_dict[y]['key']['clicks']), 
								int(backer_dict[x]['key']['clicks'])
								)
							)

		kb_base_short = app.config['KB_BASE_SHORT']

		awesm_url = ''
		kb_type = ''
		if backer_arg:
			print backer_arg, project['kb_creator']
			if project['kb_creator'] == backer_arg:
				kb_type = 'owner'
				awesm_url = project['awesm_url']
			else:
				kb_type = 'backer'
				my_backer_dict = datalib.get_backer(app.rs, backer_arg)
				awesm_url = my_backer_dict['awesm_url']


		return render_template('show_leaderboard.html',
									project = project,
									backers = backer_dict,
									sorted_backers = sorted_backers,
									total_clicks = total_clicks,
									kb_type = kb_type,
									share = share,
									awesm_url = awesm_url,
									kb_base_short = kb_base_short )
