# -*- coding: utf-8 -*-
from flask import render_template

from kickbacker import app


def respond_index(project=None):
	return render_template('get_project.html', project=project)

def get_project(project_id):
	return app.rs.hgetall('project:%s' % (project_id))

def get_backer(backer_id):
	return app.rs.hgetall('backer:%s' % (backer_id))

def show_backer(backer):
	backer_dict = get_backer(backer)
	return render_template('show_backer.html', 
								backer = backer_dict )

def show_backers(project_id):
		backers = {}
		backer_list = app.rs.smembers('project:%s:backers' % (project_id))
		for backer in backer_list:
			backers[backer] = get_backer(backer)

		project = get_project(project_id)

		return render_template('show_backers.html', 
									backer_list = backers,
									project = project )

