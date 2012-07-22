
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

# Key Redirect - key:<id>:redirect
def add_redirect(rs, key, url):
	return rs.set('key:%s:redirect' % key, url)

def get_redirect(rs, key):
	return rs.get('key:%s:redirect' % key)

