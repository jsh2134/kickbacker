from kickbacker import app
from kickbacker import views
from flask import request
import logging

@app.route('/')
@app.route('/new/')
@app.route('/new/<project>/')
def respond_index(project=None):
	return views.respond_index(project)

@app.route('/backer/<backer_id>/')
def respond_backers(backer_id):
	return views.show_backer(backer_id)

@app.route('/project/<project_id>/backers/')
def respond_show_backers(project_id):
	return views.show_backers(project_id)

@app.route('/project/backers', methods=['POST'])
def respond_get_backers():
	return views.get_project_backers()

@app.route('/project/<project_id>/prizes/')
def respond_prizes(project_id):
	return views.show_prizes(project_id)

@app.route('/project/<project_id>/edit/')
def respond_project_edit(project_id):
	return views.edit_project(project_id)

@app.route('/project/<project_id>/save/', methods=['POST'])
def respond_project_save(project_id):
	return views.save_project(project_id, request.form['kickback_id'])

@app.route('/projects/')
def respond_projects():
	return views.show_projects()

@app.route('/key/', methods=['POST'])
def respond_add_key():
	return views.new_short_key()

@app.route('/r/<project_id>/<backer_id>/')
def respond_redirect(project_id, backer_id):
	return views.key_redirect(project_id, backer_id)

@app.route('/admin/dashboard/')
def respond_dashboard():
	return views.dashboard()

@app.route('/projectboard/')
def respond_projectboard():
	return views.projectboard()

@app.route('/<project_id>/leaderboard/', methods=['GET'])
def respond_leaderboard(project_id):
	return views.leaderboard(project_id,request.values.get('url'))

@app.route('/<project_id>/leaderboard/<backer_arg>/share/', methods=['GET'])
def respond_leaderboard_share(project_id, backer_arg=None):
	return views.leaderboard(project_id, share=True, \
					backer_arg = backer_arg)


@app.route('/contact/')
def respond_contact():
	return views.respond_contact()

@app.route('/error/')
def force_error():
	logging.error('Some Error')
	try:
		print jeff
	except:
		logging.exception('Some Error')
	return views.respond_contact()

