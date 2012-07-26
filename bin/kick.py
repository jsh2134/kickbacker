#!/usr/bin/env python
import sys

from kickbacker import app
from kickbacker import kickstarter

def main():
	
	try:
		key = sys.argv[1]
		if key == 'search_projects':
			url = sys.argv[2]
			dispatch = kickstarter.get_projects
		elif key == 'project_backers':
			url = sys.argv[2]
			dispatch = kickstarter.get_backers
		elif key == 'backers_projects':
			url = sys.argv[2]
			dispatch = kickstarter.get_backer_projects
	except Exception as e:
		print e[0]
		print """ Usage:
			kick.py search_projects <search_term>
			kick.py project_backers <project url>
			kick.py backers_projects <backer url>
			"""
		sys.exit(1)

	dispatch(url)
	print "Done with %s" % key

if __name__ == '__main__':
	main()
