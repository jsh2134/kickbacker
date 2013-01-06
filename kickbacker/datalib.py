#######################
# Kickbacker Methods
#######################

# Kickbacker
def add_kickbacker(rs, email):
	""" Add a Kickbacker """
	rs.sadd('kickbacker', email)

def get_kickbackers(rs):
	""" Return all kickbackers"""
	rs.smembers('kickbacker')

def update_kickbacker(rs, email, key, value):
	""" Add metadata to Kickbacker """
	rs.hset('kickbacker:%s' % email, key, value)

def get_kickbacker(rs, email):
	""" Return metadata for KickBacker"""
	rs.hgetall('kickbacker:%s' % email)


#####################
# Project Methods
#####################

# Project List - project
def get_projects(rs):
	""" Return List of projects """
	return rs.smembers('project')

def add_project(rs, project_id):
	""" Add Project """
	return rs.sadd('project', project_id)

# Project Object - project:<id>
def get_project(rs, project_id):
	""" Return project metadata """
	return rs.hgetall('project:%s' % (project_id))

def update_project(rs, project_id, key, value):
	""" Add Metadata to a project """
	return rs.hset("project:%s" % project_id, key, value)

def increment_project_value(rs, project_id, value, inc=1):
	"""Increment project value by inc"""
	return rs.hincrby('project:%s' % project_id, value, inc)

def add_project_backer(rs, project_id, backer_id):
	""" Add a backer to a project"""
	return rs.sadd('project:%s:backers' % (project_id), backer_id)

def get_project_backers(rs, project_id):
	""" Return project backers """
	return rs.smembers('project:%s:backers' % (project_id))

def add_project_short_key(rs, project_id, key):
	""" Add a shortened url to a project"""
	return rs.sadd('project:%s:keys' % (project_id), key)

def get_project_short_keys(rs, project_id):
	""" Return project shortened urls """
	return rs.smembers('project:%s:keys' % (project_id))

def add_project_prize(rs, project_id, prize):
	""" Add a prize to a project"""
	return rs.sadd('project:%s:prizes' % (project_id), prize)

def get_project_prizes(rs, project_id):
	""" Return project shortened urls """
	return rs.smembers('project:%s:prizes' % (project_id))

def add_project_backer_prize(rs, project_id, prize):
	""" Add a prize to a project"""
	return rs.sadd('project:%s:backer_prize' % (project_id), prize)

def get_project_backer_prize(rs, project_id):
	""" Return project shortened urls """
	return rs.smembers('project:%s:backer_prize' % (project_id))


#################
# Backer Methods
#################

# Backers - backer
def add_backer(rs, backer_id):
	""" Add Backer """
	return rs.sadd('backer', backer_id)

def get_backers(rs):
	""" Return List of Backers"""
	return rs.smembers('backer')

# Backer object - backer:<id>
def update_backer(rs, backer_id, key, val):
	""" Updata Backer Metadata """
	return rs.hset('backer:%s' % (backer_id), key, val )

def get_backer(rs, backer_id):
	""" Get Backer Metadata """
	return rs.hgetall('backer:%s' % (backer_id))

def increment_backer_value(rs, backer_id, value, inc=1):
	"""Increment backer value by inc"""
	return rs.hincrby('backer:%s' % backer_id, value, inc)

# Backer object - backer:keys:<id>
def add_backer_short_key(rs, backer_id, key):
	""" Add Backer Key """
	return rs.sadd('backer:%s:keys' % (backer_id), key)

def get_backer_short_keys(rs, backer_id):
	""" Get Backer Metadata """
	return rs.smembers('backer:%s:keys' % (backer_id))


#################################
# Key (shortened URL) Methods
##################################

# Keys - key
def add_short_key(rs, key_id):
	""" Add Key """
	return rs.sadd('key', key_id)

def get_short_keys(rs):
	""" Return List of Keys"""
	return rs.smembers('key')

# Key - key:<id>
def update_short_key(rs, key_id, key, val):
	""" Update Key metadat """
	return rs.hset('key:%s' % key_id, key, val)

def get_short_key(rs, key_id):
	""" Return Key Metadata """
	return rs.hgetall('key:%s' % key_id)

def increment_short_key_value(rs, key_id, value, inc=1):
	"""Increment key value by inc"""
	return rs.hincrby('key:%s' % key_id, value, inc)

def add_short_key_referrer(rs, key_id, referrer):
	""" Log referrer of a key """
	return rs.rpush('key:%s:referrer' % key_id, referrer)

def get_short_key_referrer_list(rs, key_id):
	""" Log referrer of a key """
	print "key:%s:referrer" % key_id
	return rs.lrange('key:%s:referrer' % key_id, 0, -1)

# Key Redirect - key:<id>:redirect
def add_redirect(rs, key, url):
	return rs.set('key:%s:redirect' % key, url)

def get_redirect(rs, key):
	return rs.get('key:%s:redirect' % key)

# Key Rewards - key:<id>:reward
def add_rewards(rs, key, reward):
	return rs.hset('key:%s:rewards' % key, reward, 1)

def incr_rewards(rs, key, reward, inc=1):
	return rs.hincrby('key:%s:rewards' % key, reward, inc)

def get_rewards(rs, key):
	return rs.hgetall('key:%s:rewards' % key)

#################################
# Prize (Backer Rewards) Methods
##################################

# Prizes - prize
def add_short_prize(rs, prize_id):
	""" Add Prize """
	return rs.sadd('prize', prize_id)

def get_short_prizes(rs):
	""" Return List of Prizes"""
	return rs.smembers('prize')

# Prize - prize:<id>
def update_short_prize(rs, prize_id, key, val):
	""" Update Prize metadata """
	return rs.hset('prize:%s' % prize_id, key, val)

def get_short_prize(rs, prize_id):
	""" Return Prize Metadata """
	return rs.hgetall('prize:%s' % prize_id)

