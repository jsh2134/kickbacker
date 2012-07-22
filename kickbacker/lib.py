
def update_project(rs, project_id, key, value):
	return rs.hset("project:%s" % project_id, key, value)

def add_project_backer(rs, project_id, backer_id):
	return rs.sadd('project:%s:backers' % (project_id), backer_id)

def update_backer(rs, backer_id, key, val):
	return rs.hset('backer:%s' % (backer_id), key, val )

