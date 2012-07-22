#!/usr/bin/env python
import sys

#from kickbacker import app
from kickbacker import kickstarter

def main():
	
	#try:
	rs = app.rs
	#except:
	#	import redis
	#	rs = redis.Redis('localhost')
		

	key = sys.argv[1]

	if key == 'search_projects':
		search_key = sys.argv[2]
		kickstarter.get_projects(rs, search_key)
	elif key == 'project_backers':
		url = sys.argv[2]
		kickstarter.get_backers(rs, url)
	elif key == 'backers_projects':
		url = sys.argv[2]
		kickstarter.get_backer_projects(rs, url)

if __name__ == '__main__':
	try:
		main()
	except:
		print """ Usage:
			kick.py search_projects <search_term>
			kick.py project_backers <project url>
			kick.py backers_projects <backer url>
			"""
