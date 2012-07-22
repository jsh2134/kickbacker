# -*- coding: utf-8 -*-
import datetime

from flask import render_template
from flask import request
from flask import jsonify
from flask import redirect

from kickbacker import app
from kickbacker import datalib
from kickbacker import kickstarter

def respond_index(project=None):
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
	raw_key = request.values.get('awesm')
	key = raw_key.split('_')[1]
	app.logger.info("%s %s" % (raw_key, key))
	redirect_url = datalib.get_redirect(app.rs, key)
	app.logger.info("Redirecting to %s" % (redirect_url) )
	# TODO set some cookies with the project and backer ids
	return redirect(redirect_url)


def add_short_key():
	key = request.form.get('key')
	url = request.form.get('url')
	kb_url = request.form.get('kb_url')
	backer_id = request.form.get('backer_id')
	project_id = request.form.get('project_id')

	# TODO queue up backer scrape job
	datalib.add_backer(app.rs, backer_id)
	# TODO queue up project scrape job
	datalib.add_project(app.rs, project_id)

	datalib.add_short_key(app.rs, key)
	datalib.add_backer_short_key(app.rs, backer_id, key)
	datalib.add_project_short_key(app.rs, project_id, key)
	datalib.add_redirect(app.rs, key, url)
	datalib.update_short_key(app.rs, key, 'clicks', 0)
	datalib.update_short_key(app.rs, key, 'url', url)
	datalib.update_short_key(app.rs, key, 'created', datetime.datetime.now())
	datalib.update_short_key(app.rs, key, 'project_id', project_id)
	datalib.update_short_key(app.rs, key, 'backer_id', backer_id)

	return jsonify( {   'success':True, 
						'message':'Added key:%s for backer:%s to project:%s' \
									% (key, backer_id, project_id)})


