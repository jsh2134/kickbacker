from kickflask import KickFlask
app = KickFlask(__name__)
app.config.from_object('kickbacker.settings.DevConfig')

app.connect_redis()
app.set_logging()

import urls


