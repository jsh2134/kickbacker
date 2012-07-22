from kickflask import KickFlask
app = KickFlask(__name__)
app.config.from_object('kickbacker.settings.DevConfig')

app.setup_logging()
app.connect_redis()

import urls


