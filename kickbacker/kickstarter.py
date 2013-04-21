# -*- coding: utf-8 -*-
import urllib
import json
import re
import time
import logging
import hashlib
import HTMLParser
from types import StringType

logging.basicConfig(filename='/var/log/kickbacker.log', level=logging.INFO)

import BeautifulSoup

from kickbacker import app
from kickbacker import datalib
from kickbacker import lib
from kickbacker import defaults

KS_ROOT = 'http://www.kickstarter.com'
BACKER_URL = KS_ROOT + '/profile/%s'


def get_kickstarter_response(url, json_out=True):
	logging.info("Hitting %s" % url)
	try:
		result = urllib.urlopen(url)
	except IOError:
		logging.info('IOError, trying twice more')
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


def unescape_html(value):
	
	if not value or not type(value) == StringType:
		return value

	try:
		h = HTMLParser.HTMLParser()
		unescaped = h.unescape(value)
	except:
		logging.exception("Could not escape: %s" % value)
		unescaped = value

	return unescaped



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

	backer = defaults.BACKER
	backer['id'] = backer_id
	backer['url'] = BACKER_URL % (backer_id)
			
	try:
		img_div = soup.findAll("meta", {"property":"og:image"})
		logging.info(img_div)
		backer['img'] = find_attr('content', img_div[0].attrs)
	except:
		logging.exception("Could not find backer 'img' attr")
		logging.exception(str(img_div))

	try:
		name_div = soup.findAll("meta", {"property":"og:title"})
		logging.info(name_div)
		backer['name'] = find_attr('content', name_div[0].attrs).replace('on Kickstarter','').strip()
	except:
		logging.exception("Could not find backer 'name' attr")
		logging.exception(str(name_div))

	try:
		loc_div = soup.findAll("div", {"class":"location"})
		logging.info(loc_div)
		backer['location'] = loc_div[0].contents[1].strip()
	except:
		logging.exception("Could not find backer 'location' attr")
		logging.exception(str(loc_div))

	try:
		bio_div = soup.findAll("div", {"class":"bio"})
		logging.info(bio_div)
		backer['bio'] = bio_div[0].p.contents[0].strip()
	except:
		logging.exception("Could not find backer 'bio' attr")
		logging.exception(str(bio_div))

	return backer


def parse_project_page(project_id, soup):
	""" Parse a single project page identified by its URL
	
	**Arguments**
		:project_id: id of the project
		:soup: BeautifulSoup'd response object

	**Returns**
		A dictionary of project attributes
	"""

	project = defaults.PROJECT
	project['id'] = project_id

	try:
		name_div = soup.findAll("meta", {"property":"og:title"})
		project['name'] = find_attr('content', name_div[0].attrs)
		project['title'] = find_attr('content', name_div[0].attrs)
	except:
		logging.exception("Could not find project 'name' and 'title' attr")
		logging.exception(str(name_div))

	try:
		url_div = soup.findAll("meta", {"property":"og:url"})
		project['link'] = find_attr('content', url_div[0].attrs)
	except:
		logging.exception("Could not find project 'url' attr")
		logging.exception(str(url_div))

	try:
		desc_div = soup.findAll("meta", {"property":"og:description"})
		project['desc'] = find_attr('content', desc_div[0].attrs)
	except:
		logging.exception("Could not find project 'desc' attr")
		logging.exception(str(desc_div))

	author_a = soup.findAll('a', {'data-modal-class':'modal_project_by'})
	if not author_a:
		logging.exception("Could not find project 'author' attr")
	else:
		try:
			project['author'] = author_a[0].contents[0]
		except:
			logging.exception("Could not parse project 'author' attr")
			logging.exception(str(author_a))

		try:
			project['author_link'] = \
						find_attr('href', author_a[0])
		except:
			logging.exception("Could not find project 'author_link' attr")
			logging.exception(str(author_a))
	

	try:
		desc_p_long = soup.findAll('div',\
					 {'class':'full-description'})[0].p.contents[0]
		project['desc_full'] = desc_p_long
	except Exception:
		logging.exception("Could not find project 'desc_full' attr")

	try:
		project['started'] = soup.findAll('li', {'class':'posted'})[0].contents[2].strip('\n ')
	except:
		logging.exception("Could not find project 'started' attr")

	try:
		project['end'] = soup.findAll('li', \
					{'class':'ends'})[0].contents[2].strip('\n ')
	except:
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
		logging.exception("Could not find project 'img' attr")

	try:
		loc_div = soup.findAll('li', {'class':'location'})[0]
		project['loc'] = loc_div.a.contents[1].strip()
	except:
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

		logging.info('this is pct-funded %s' % project['pct-funded'])
		if 'pct-funded' in project and project['pct-funded']:
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


	# Get Project Rewards (prizes)
	prizes = []
	logging.info('\n\nPrizes')
	prize_ul = soup.findAll('ul', {'id':'what-you-get'})
	prize_lis = prize_ul[0].findAll('li')
	for li in prize_lis:
		prize = {}
		try:
			prize['title'] = li.h5.contents[0].strip()
		except:
			logging.exception('Problem parsing prize_li: %s' % str(li))
		# strip commas and match digits
		prize['value'] = re.compile('.*[$£](\d+).*').match(prize['title'].replace(',','')).groups()[0]
		prize['id'] = create_prize_id(project_id, prize['title'])

		try:
			prize['link'] = find_attr('href', li.attrs)
		except:
			logging.exception('Cant find link for this prize')
		logging.info(prize)

		try:
			desc_div = li.findAll('div', {'class':'desc'})
			desc_str = ""
			for s in desc_div[0].contents:
				desc_str += s.string.strip()
			prize['desc'] = unescape_html(desc_str.strip())
		except:
			logging.exception('Cant find descrip for this prize')

		try:
			deliv_div = li.findAll('div', {'class':'delivery-date'})
			prize['delivery-date'] = deliv_div[0].contents[0].strip("\n ")
		except:
			logging.exception('Cant find deliv_date for this prize')

		# Append prize to list of prizes
		prizes.append(prize)

	if prizes:
		project['prizes'] = prizes

	return project


def create_prize_id(project_id, name):
	return hashlib.sha224(project_id + "kb" + name).hexdigest()[:8]
	#prize_id = re.compile('.*backer_reward_id%5D=(\d+).*').match(url)
	#if prize_id:
	#	return prize_id.groups()[0]
	#else:
	#	logging.info('No backer_reward_id found in %s' % url)
	#	return None


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


def add_prizes(prizes, project_id):
	""" Add prizes to a project """
	for prize in prizes:
		datalib.add_prize(app.rs, prize['id'])
		datalib.add_project_prize(app.rs, project_id, prize['id'])
		for key, value in prize.iteritems():
			a = datalib.update_prize(app.rs, prize['id'], key, unescape_html(value))
			logging.info('Prizes: %s %s: %s' % ("Added" if a else "Existed", key, value))

	# Add some prize at the end
	# signals that all prizes have been stored
	datalib.update_project(app.rs, project_id, 'backer_prize', prize['id'])

	return True


def is_valid_scrape(obj_dict, reqs):

	# Valid Keys present
	#if set(reqs).intersection(set(obj_dict.keys())) == reqs:
		# Keys not False or blank
		for key in reqs:
			if not obj_dict[key]:
				logging.info('%s is not valid %s' % (key, obj_dict[key]))
				return False
		return True
		logging.info(obj_dict.keys())
		logging.info(reqs)
		return False

def get_project(project_url):
	logging.info("Parsing URL %s" % (project_url) )
	project_id = get_project_id(project_url)

	resp = get_kickstarter_response(project_url, json_out=False)
	soup = BeautifulSoup.BeautifulSoup(resp)

	project_dict = parse_project_page(project_id, soup)
	for key, value in project_dict.iteritems():
		if key == 'prizes':
			a = add_prizes(project_dict['prizes'], project_id)
		else:	
			a = datalib.update_project(app.rs, project_id, key, unescape_html(value))
	
		logging.info('%s %s: %s' % ("Added" if a else "Existed", key, value))

	# Finalize Scrape
	if is_valid_scrape(project_dict, ['name', 'title', 'link', 'prizes', 'img']):
		datalib.update_project(app.rs, project_id, 'scraped', 1)

	return project_dict


def is_scrape_complete(type_obj, type_id):
	""" Return True, is 'scraped' value has been added at end of scrape routines"""
	if type_obj == 'project':
		obj_get = datalib.get_project
	else:
		obj_get = datalib.get_backer

	my_obj = obj_get(app.rs, type_id)

	if my_obj and 'scraped' in my_obj and int(my_obj['scraped']) == 1:
		return True
	else:
		return False


def get_backer(backer_url):
	logging.info("Parsing URL %s" % (backer_url) )

	resp = get_kickstarter_response(backer_url, json_out=False)
	soup = BeautifulSoup.BeautifulSoup(resp)

	backer_id = get_backer_id(backer_url, full_url=True)

	backer_dict = parse_backer_page(backer_id, soup)
	for key, value in backer_dict.iteritems():
		a = datalib.update_backer(app.rs, backer_id, key, unescape_html(value))
		logging.info('%s %s: %s for %s' % ("Added" if a else "Existed", key, value, backer_id))
	
	# Finalize Scrape
	if is_valid_scrape(backer_dict, ['name', 'img']):
		datalib.update_backer(app.rs, backer_id, 'scraped', 1)
	else:
		logging.info('NOT VALID!!!')

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

#############
# Not in Use
#############
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

