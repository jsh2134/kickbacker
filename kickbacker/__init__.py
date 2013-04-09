from kickflask import KickFlask
import local_settings

app = KickFlask(__name__)

if local_settings.ENV == 'production':
	app.config.from_object('settings.ProdConfig')
else:
	app.config.from_object('settings.DevConfig')

app.setup_logging()
app.connect_redis()

import urls


