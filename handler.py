from kickbacker import app

app.run(host=app.config['HOST'],
		debug=app.config['DEBUG'])


