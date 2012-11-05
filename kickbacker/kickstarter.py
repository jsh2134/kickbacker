import urllib
import json
import re
import time
import logging

logging.basicConfig(filename='/var/log/kickbacker.log', level=logging.INFO)

import BeautifulSoup

from kickbacker import app
from kickbacker import datalib
from kickbacker import lib

KS_ROOT = 'http://www.kickstarter.com'
BACKER_URL = KS_ROOT + '/profile/%s'


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
	for attr in attr_list:
		if attr[0] == attr_name:
			return attr[1]
	logging.debug("Attr Lookup - could not find <%s> in %s" % \
							(attr_name, attr_list))
	return None

def get_backer_id(url, full_url=True):
       """ URL is in the form /profile/<id or name>/ unless full_url is pasesed
               For now we will assume this is unique """
       if full_url:
               id_match = re.compile('.*\/profile\/(\w+)\/?.*')
               find_bid = id_match.match(url)
               return find_bid.groups()[0]
       else:
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


#############################
# Parsers
#############################

def parse_backer_page(backer_id, soup):
	""" Parse a single backer page identified by its URL
	
	**Arguments**
		:backer_id: id of the backer
		:soup: BeautifulSoup'd response object

	**Returns**
		A dictionary of backer attributes
	"""

	backer = { 'id': backer_id,
			   'url': BACKER_URL % (backer_id)
			}
	logging.info(soup)
	try:
		img_div = soup.findAll("meta", {"property":"og:image"})
		#img_div = soup.findAll("div", {"id":"profile-avatar"})
		logging.info(img_div)
		backer['img'] = find_attr('content', img_div[0].attrs)
	except:
		logging.exception("Could not find backer 'img' attr")
		logging.exception(str(img_div))
		backer['img'] = ''

	try:
		name_div = soup.findAll("meta", {"property":"og:title"})
		logging.info(name_div)
		backer['name'] = find_attr('content', name_div[0].attrs).replace('on Kickstarter','').strip()
		#name_div = soup.findAll("div", {"id":"profile-bio"})
		#backer['name'] = name_div[0].h1.contents[0].replace('\n','').strip()
	except:
		logging.exception("Could not find backer 'name' attr")
		logging.exception(str(name_div))
		backer['name'] = ''

	try:
		loc_div = soup.findAll("div", {"class":"location"})
		logging.info(loc_div)
		backer['location'] = loc_div[0].contents[1].strip()
	except:
		logging.exception("Could not find backer 'location' attr")
		logging.exception(str(loc_div))
		backer['location'] = ''

	try:
		bio_div = soup.findAll("div", {"class":"bio"})
		logging.info(bio_div)
		backer['bio'] = bio_div[0].p.contents[0].strip()
	except:
		logging.exception("Could not find backer 'bio' attr")
		logging.exception(str(bio_div))
		backer['bio'] = ''

	return backer


def parse_project_page(project_id, soup):
	""" Parse a single project page identified by its URL
	
	**Arguments**
		:project_id: id of the project
		:soup: BeautifulSoup'd response object

	**Returns**
		A dictionary of project attributes
	"""

	project = { 'id': project_id }

	name_h1 = soup.findAll('h1', {'id':'title'})[0]
	project['name'] = name_h1.a.contents[0]
	project['title'] = name_h1.a.contents[0]
	project['link'] = find_attr('href', name_h1.a.attrs)

	author_a = soup.findAll('div', {'id':'creator-name'})
	if author_a:
		try:
			project['author'] = author_a[0].h3.a.contents[0]
		except:
			logging.exception("Could not find project 'author' attr")
			logging.exception(str(author_a))
			project['author'] = ''

		try:
			project['author_link'] = \
						find_attr('href', author_a[0].h3.a.attrs)
		except:
			logging.exception("Could not find project 'author_link' attr")
			project['author_link'] = ''
	else:
		project['author'] = ''
		logging.exception("Could not find project 'author' attr")
	

	try:
		desc_p = soup.findAll('p', \
					 {'class':'short-blurb'})[0].contents[0]
	except Exception:
		desc_p = ''
		logging.exception("Could not find project 'desc' attr")

	project['desc'] = desc_p

	try:
		desc_p_long = soup.findAll('div',\
					 {'class':'full-description'})[0].p.contents[0]
	except Exception:
		desc_p_long = ''
		logging.exception("Could not find project 'desc_full' attr")
	project['desc_full'] = desc_p_long

	try:
		project['started'] = soup.findAll('li', {'class':'posted'})[0].contents[2].replace('\n','')
	except:
		project['started'] = ''
		logging.exception("Could not find project 'started' attr")

	try:
		project['end'] = soup.findAll('li', \
					{'class':'ends'})[0].contents[2].replace('\n','')
	except:
		project['end'] = ''
		logging.exception("Could not find project 'end' attr")

	try:
		video_notifier_div = soup.findAll('div', {'data-has-video': 'false'})
		if video_notifier_div:
				project['img'] = \
					find_attr('src', video_notifier_div[0].img.attrs)
		else:
			video_div = soup.findAll('div', {'class':'video-player'})
			if video_div:
				project['img'] = \
						find_attr('data-image', video_div[0].attrs)
				project['video'] = \
						find_attr('data-video', video_div[0].attrs)
	except:
		project['img'] = ''
		logging.exception("Could not find project 'img' attr")

	try:
		loc_div = soup.findAll('li', {'class':'location'})[0]
		project['loc'] = loc_div.a.contents[1].strip()
	except:
		project['loc'] = ''
		logging.exception("Could not find project 'loc' attr")


	number_divs = soup.findAll('div', {'class':'num'})
	for nd in number_divs:
		if find_attr('data-backers-count', nd.attrs):
			project['backers_count'] = \
						find_attr('data-backers-count', nd.attrs)
		if find_attr('data-goal', nd.attrs):
			project['goal'] = \
						find_attr('data-goal', nd.attrs)
		if find_attr('data-percent-raised', nd.attrs):
			project['pct-funded'] = \
						find_attr('data-percent-raised', nd.attrs)

		if 'pct-funded' in project:
			if float(project['pct-funded']) < 1.0:
				project['status'] = "Raising"
				project['funded'] = False
			else:
				project['status'] = "Funded"
				project['funded'] = True

		if find_attr('data-pledged', nd.attrs):
			project['amount'] = \
						find_attr('data-pledged', nd.attrs)

	number_divs = soup.findAll('span', {'id':'project_duration_data'})
	for nd in number_divs:
		if find_attr('data-end_time', nd.attrs):
			project['end_time'] = \
						find_attr('data-end_time', nd.attrs)
		if find_attr('data-hours_remaining', nd.attrs):
			project['hours_left'] = \
						find_attr('data-hours_remaining', nd.attrs)

	return project


def parse_project_results_json(js):
	""" Parse a group of projects returned via JSON call
	
	**Arguments**
		:js: JSON response object

	**Returns**
		A dictionary projects and their attributes
	"""
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
		url = lib.strip_url_args(url)

		pid = get_project_id(url)

		projects_dict[pid] = {  'name' : name,
								'url' : url,
							 }


def parse_backers(backer_list, backer_dict):
	""" Given a Project URL, parse a list of backers and find their respective
		attributes
	"""
	for backer in backer_list:
		img = find_attr(u'src', backer.a.img.attrs)
		url = find_attr(u'href', backer.a.attrs)
		url = lib.strip_url_args(url)
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


def get_project(project_url):

	logging.info("Parsing URL %s" % (project_url) )

	resp = get_kickstarter_response(project_url, json_out=False)
	soup = BeautifulSoup.BeautifulSoup(resp)

	project_id = get_project_id(project_url)
	project_dict = parse_project_page(project_id, soup)
	for key, value in project_dict.iteritems():
		a = datalib.update_project(app.rs, project_id, key, value)
		logging.info('%s %s: %s' % ("Added" if a else "Existed", key, value))
	
	return project_dict


def get_backer(backer_url, backer_type):

	logging.info("Parsing URL %s" % (backer_url) )

	resp = get_kickstarter_response(backer_url, json_out=False)
	soup = BeautifulSoup.BeautifulSoup(resp)

	backer_id = get_backer_id(backer_url, full_url=True)

	backer_dict = parse_backer_page(backer_id, soup)
	for key, value in backer_dict.iteritems():
		a = datalib.update_backer(app.rs, backer_id, key, value)
		logging.info('%s %s: %s for %s' % ("Added" if a else "Existed", key, value, backer_id))
	
	# Add Backer Type 
	datalib.update_backer(app.rs, backer_id, 'type', backer_type)

	return backer_dict


def get_projects(search_key):
	base_url = "http://www.kickstarter.com/%s/search.json?utf8=&term=%s"

	url = base_url % ('projects', search_key)
	logging.info("Searching with URL %s" % (url) )

	js = get_kickstarter_response(url)
	project_map = parse_project_results_json(js)

	for project in project_map:
		for key, value in project_map[project].iteritems():
			a = datalib.update_project(app.rs, project, key, value)
			logging.info('%s %s: %s' % ("Added" if a else "Existed", key, value))
	
	return project_map


def get_backers(url):

	url = lib.strip_url_args(url)
	logging.info( "Getting backers for %s" % (url) )

	backer_url = "%s/backers?page=%s"
	backer_tag = 'NS-backers-backing-row'
	backer_index = 1
	max_backers = 100
	backer_dict = {}

	project_id = get_project_id(url)
	datalib.add_project(app.rs, project_id)

	while True:
		
		backer_html = get_kickstarter_response(backer_url % \
								(url, backer_index) , json_out = False)
		soup = BeautifulSoup.BeautifulSoup(backer_html)
		backers = soup.findAll("div", {'class': backer_tag})
		if not backers:
			logging.info("Found no backers on page %s" % (backer_index))
			break
		else:
			logging.info("Found %s backers on page %s" % \
								(len(backers), backer_index) )
			parse_backers(backers, backer_dict)
			backer_index+=1

			if len(backer_dict) >= max_backers:
				logging.info('hit %s backers, breaking out of loop' % \
														max_backers)
				break 

			# Sleep for two seconds
			logging.info('%s backers found' % len(backer_dict))
			time.sleep(1)
	
	for backer_id in backer_dict:
		backer_success = datalib.add_backer(app.rs, backer_id)
		success = datalib.add_project_backer(app.rs, project_id, backer_id)
		for key, val in backer_dict[backer_id].iteritems():
			a = datalib.update_backer(app.rs, backer_id, key, val )
			logging.info('%s %s: %s' % ("Added" if a else "Existed", key, val))

	return project_id, backer_dict

def get_backer_projects(url):

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
			if len(projects_dict) >= max_projects:
				logging.info("Reached %s projects, exiting" % max_projects)
				break

			logging.info('%s projects found' % len(projects_dict))
			# Sleep for two seconds
			time.sleep(1)

	for project_id in projects_dict:
		datalib.add_project(app.rs, project_id)
		for key, value in projects_dict[project_id].iteritems():
			datalib.update_project(app.rs, project_id, key, value)

	return projects_dict

