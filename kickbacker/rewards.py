from kickbacker import datalib
from kickbacker import app


def url_check(urls, referrer):
	for url_val in urls:
		if url_val in referrer:
			return True
	return False


def check_for_rewards(key_id, referrer):
	for reward_key, reward_vals in REWARD_MAP.iteritems():
		if reward_vals['func'](referrer):
			if reward_vals['type'] == 'incr':
				datalib.incr_rewards(app.rs, key_id, reward_key)
			else:
				datalib.add_rewards(app.rs, key_id, reward_key)
	return True


def is_twitter_reward(referrer):
	urls = ['twitter.com', 't.co']
	return url_check(urls, referrer)


def is_facebook_reward(referrer):
	urls = ['facebook.com', 'fb.com']
	return url_check(urls, referrer)


def is_youtube_reward(referrer):
	urls = ['youtube.com', 'youtu.be']
	return url_check(urls, referrer)


# reward_key : reward_check_function
REWARD_MAP = {
	'twitter' : { 'func': is_twitter_reward,
				  'desc': 'Referral Came from Twitter',
				  'type': 'incr'
				},
	'facebook' : { 'func': is_facebook_reward,
				   'desc': 'Referral Came from Facebook',
				   'type': 'incr'
				},
	'youtube' : { 'func': is_youtube_reward,
				  'desc': 'Referral Came from YouTube',
				  'type': 'incr'
				},
}

