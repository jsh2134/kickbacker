from kickbacker import app
from kickbacker import views

@app.route('/')
@app.route('/new/')
@app.route('/new/<project>')
def respond_index(project=None):
	return views.respond_index(project)

@app.route('/backer/<backer_id>')
def respond_backers(backer_id):
	return views.show_backer(backer_id)

@app.route('/project/<project_id>/backers/')
def respond_show_backers(project_id):
	return views.show_backers(project_id)

@app.route('/project/backers', methods=['POST'])
def respond_get_backers():
	return views.get_project_backers()

@app.route('/projects')
def respond_projects():
	return views.show_projects()

@app.route('/key', methods=['POST'])
def respond_add_key():
	return views.add_short_key()

@app.route('/r/<project_id>/<backer_id>/')
def respond_redirect(project_id, backer_id):
	return views.key_redirect(project_id, backer_id)

@app.route('/admin/dashboard')
def respond_dashboard():
	return views.dashboard()

@app.route('/projectboard')
def respond_projectboard():
	return views.projectboard()

@app.route('/<project_id>/leaderboard')
def respond_leaderboard(project_id):
	return views.leaderboard(project_id)

