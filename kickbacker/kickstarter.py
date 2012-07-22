import urllib
import json
import re
import time
import logging

import BeautifulSoup

from kickbacker import lib

def get_kickstarter_response(url, json_out=True):
	logging.info("Hitting %s" % url)
	result = urllib.urlopen(url)
	resp = result.read()
	if json_out:
		return json.loads(resp)
	else:
		return resp


def find_attr(attr_name, attr_list):
	""" Given a list of attribute tuples, return the value
		of the attribute attr_name or None if not found
	"""
	logging.info("Looking for <%s> in %s" % (attr_name, attr_list))
	for attr in attr_list:
		if attr[0] == attr_name:
			return attr[1]
	return None


def get_backer_id(url):
	""" URL is in the form /profile/<id or name>/ 
		For now we will assume this is unique """
	return url.replace('/profile/', '')


def get_project_id(url):
	id_match = re.compile('.*\/projects\/(\w+)\/.*')
	find_pid = id_match.match(url)
	if find_pid:
		pid = find_pid.groups()[0]
	else:
		logging.info('could not find a pid in %s' % (url))
		pid = url

	return pid


def parse_project(js):
	projects = {}
	for project in js['projects']:
		projects[project['id']] = {	
									'name': project['name'],
									'raw_card': project['card_html']
								}
		soup = BeautifulSoup.BeautifulSoup(project['card_html'])
		divs = soup.div.div.findAll('div')
		projects[project['id']]['link'] = divs[0].a.attrs[0][1]
		projects[project['id']]['img'] = divs[0].img.attrs[3][1]
		projects[project['id']]['status'] = divs[1].strong.contents[0]

		divs = soup.div.findAll('div')
		projects[project['id']]['title'] = divs[0].h2.strong.a.contents[0]
		projects[project['id']]['desc'] = divs[0].p.contents[0].replace('&amp;','&')
		projects[project['id']]['author'] = divs[0].h2.span.contents[0].replace('by\n','').replace('\n','')

		uls = soup.findAll('ul')
		for ul in uls:
			if 'project-meta' in ul.attrs[0]:
				projects[project['id']]['loc'] = ul.li.a.contents[1].contents[0]

			if 'project-stats' in ul.attrs[0]:
				lis = ul.findAll('li')
				for li in lis:
					if 'first funded' in li.attrs[0]:
						projects[project['id']]['pct-funded'] = li.strong.contents[0]
					if 'pledged' in li.attrs[0]:
						projects[project['id']]['amount'] = li.strong.contents[0]
					if 'last successful' in li.attrs[0]:
						projects[project['id']]['funded'] = li.strong.contents[0]
					if 'last ksr_page_timer' in li.attrs[0]:
						projects[project['id']]['end'] = li.attrs[1][1]
	return projects


def parse_backer_projects(projects_list, projects_dict):
	""" Parse a list of projects and find their respective
		attributes
	"""
	for project in projects_list:
		name = project.div.h2.a.contents[0]
		url = find_attr(u'href', project.div.a.attrs)
		# Strip away any ref args
		if url.find('?'):
			url = url[:url.find('?')]

		pid = get_project_id(url)

		projects_dict[pid] = {  'name' : name,
								'url' : url,
							 }


def parse_backers(backer_list, backer_dict):
	""" Parse a list of backers and find their respective
		attributes
	"""
	for backer in backer_list:
		img = find_attr(u'src', backer.a.img.attrs)
		url = find_attr(u'href', backer.a.attrs)
		key = get_backer_id(url)
		name = backer.div.a.contents[0]
		note_res = backer.findAll('div', {'class': 'note'})
		if note_res:
			note = note_res[0].contents[0]
		else:
			logging.info("No Note Found")
			note = ''

		backer_dict[key] = {    'url' : url,
								'name' : name,
								'note' : note,
								'img' : img,
							}
		logging.info(backer_dict[key])


def get_projects(rs, search_key):
	base_url = "http://www.kickstarter.com/%s/search.json?utf8=&term=%s"

	url = base_url % ('projects', search_key)
	logging.info("Searching with URL %s" % (url) )

	js = get_kickstarter_response(url)
	project_map = parse_project(js)

	for project in project_map:
		for key, value in project_map[project].iteritems():
			a = lib.update_project(rs, project, key, value)
			logging.info('%s %s: %s' % ("Added" if a else "Existed", key, value))
	
	return project_map


def get_backers(rs, url):

	logging.info( "Getting backers for %s" % (url) )

	backer_url = "%s/backers?page=%s"
	backer_tag = 'NS-backers-backing-row'
	backer_index = 1
	max_backers = 200
	backer_dict = {}

	project_id = get_project_id(url)

	while True:
		
		backer_html = get_kickstarter_response(backer_url % (url, backer_index) , json_out = False)
		soup = BeautifulSoup.BeautifulSoup(backer_html)
		backers = soup.findAll("div", {'class': backer_tag})
		if not backers:
			logging.info("Found no backers on page %s" % (backer_index))
			break
		else:
			logging.info("Found %s backers on page %s" % (len(backers), backer_index) )
			parse_backers(backers, backer_dict)
			backer_index+=1
			
			if backer_index > max_backers:
				logging.info('hit %s backers, breaking out of loop' % max_backers)
				break 

			# Sleep for two seconds
			time.sleep(2)
	
	for backer_id in backer_dict:
		success = lib.add_project_backer(rs, project_id, backer_id)
		for key, val in backer_dict[backer_id].iteritems():
			a = lib.update_backer(backer_id, key, val )
			logging.info('%s %s: %s' % ("Added" if a else "Existed", key, val))

	return backer_dict

def get_backer_projects(rs, url):

	logging.info( "Getting projects for user %s" % (url) )
	
	# change profile to profiles
	url = url.replace('/profile/','/profiles/')
	projects_url = "%s/projects/backed?page=%s"

	projects_tag = 'project-card-wide-wrap'
	projects_index = 1
	max_projects = 100
	projects_dict = {}

	while True:
		
		projects_html = get_kickstarter_response(projects_url % (url, projects_index) , json_out = False)
		soup = BeautifulSoup.BeautifulSoup(projects_html)
		projects = soup.findAll("div", {'class': projects_tag})
		if not projects:
			logging.info("Found no projects on page %s" % (projects_index))
			break
		else:
			logging.info("Found %s projects on page %s" % (len(projects), projects_index) )
			parse_backer_projects(projects, projects_dict)
			projects_index+=1
			if projects_index > max_projects:
				logging.info("Reached %s projects, exiting" % max_projects)
				break

			# Sleep for two seconds
			time.sleep(2)
	#TODO insert into redis
	return projects_dict

