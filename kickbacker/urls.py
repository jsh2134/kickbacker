from kickbacker import app
from kickbacker import views

@app.route('/')
def respond_home():
	return views.hello_world()

@app.route('/new/<project>')
def respond_index(project):
	return views.respond_index(project)

@app.route('/backer/<backer_id>')
def respond_backers(backer_id):
	return views.show_backer(backer_id)

@app.route('/project/<project_id>/backers/')
def respond_show_backers(project_id):
	return views.show_backers(project_id)

