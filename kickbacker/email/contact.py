import logging
import time

import mandrill

from kickbacker.email import config
from kickbacker import datalib
from kickbacker import app
from kickbacker import kickstarter
from secrets import MANDRILL



def format_template_content(template_dict):
	""" Takes dictionary of key/val items and turns into
		Mandrill format of [ {"name":key , "content":val}, {...} ]"""

	template_content = []

	for key, val in template_dict.iteritems():
			template_content.append( 	{ 	'name': key,
										'content': val,
									}
								)

	return template_content


def send_mail(to, template_subject, template_content, template):

	m = mandrill.Mandrill(MANDRILL)

	vals = {
		"template_name": template['template_name'],
		"template_content": template_content,
		"message": {
			"subject": template_subject,
			"from_email": config.account_info['from_email'],
			"from_name": config.account_info['from_name'],
			"bcc_address": config.account_info['bcc'],
			"to": [
				{
					"email": to,
				}
			],
			#"headers": {
			#    "Reply-To": "message.reply@example.com"
			#},
			"track_opens": True,
			"track_clicks": True,
			"auto_text": None,
			"auto_html": None,
			"inline_css": None,
			"url_strip_qs": None,
			"preserve_recipients": None,
			"tracking_domain": None,
			"signing_domain": None,
		},
		"async": False
	}

	response = m.messages.send_template(**vals)
	print response




def send_welcome_mail(to_email, kb_type, backer_id, project_id, new_backer):

	# Get Backer data and project_data
	infinite_count = 0
	backer = kickstarter.is_scrape_complete('backer', backer_id)
	project = kickstarter.is_scrape_complete('project', project_id)

	while not backer and not project:
		backer = kickstarter.is_scrape_complete('backer', backer_id)
		project = kickstarter.is_scrape_complete('project', project_id)
		infinite_count +=1
		if infinite_count >= 30:
			logging.exception('After 30 tries backer and project are %s and %s' % \
									(backer, project))
			break
		time.sleep(5)

	# We are fully scraped now
	backer = datalib.get_backer(app.rs, backer_id)
	project = datalib.get_project(app.rs, project_id)

	if kb_type == 'owner':
		body_text = config.body_owner
		template_subject = 'Welcome to KickBacker - You are One Step Closer'
		awesm_url = project['awesm_url']
		leaderboard_url = '%s/%s/leaderboard/%s/share' % \
								 (app.config['KB_BASE'],project_id, backer_id)
	else:
		body_text = config.body_kickbacker
		template_subject = 'Welcome to KickBacker - Earn KickBacks Today'
		awesm_url = backer['awesm_url']
		leaderboard_url = '%s/%s/leaderboard/%s/share' % \
						(app.config['KB_BASE'],project_id, backer_id)

	template = config.templates['new_kb']

	template['template_values']['body_content'] = body_text % \
					{'awesm_url' : awesm_url,
					 'leaderboard' : leaderboard_url,
					 'header_image' : project['img'],
					 'project_name' : project['name'],
					}
	template_content = format_template_content(template['template_values'])

	send_mail(to_email, template_subject, template_content, template)
