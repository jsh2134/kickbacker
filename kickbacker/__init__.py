from kickflask import KickFlask
app = KickFlask(__name__)
app.config.from_object('settings.DevConfig')

app.setup_logging()
app.connect_redis()

import urls


