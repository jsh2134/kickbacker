
account_info = { 'from_email' : 'kickbacker@kickbacker.co',
				 'from_name' : 'KickBacker',
				}


body_owner =  """

<h1> Welcome to KickBacker </h1>

<img src="%(header_image)s" width="280px;">
<br>
%(project_name)s

<h2>Step 1: Share with your Backers</h2>

<h3>%(awesm_url)s</h3>

You are one step closer to a funded project. Share this link with your backers and start driving more traffic and more backers to your project. 

<h2>Step 2: Track your Progress</h2>

<h3>%(leaderboard)s</h3>

Track the progress you're backers are making by visiting your project's Leaderboard.

"""

body_kickbacker =  """

<h1> Welcome to KickBacker </h1>

<img src="%(header_image)s" width="280px;">
<br>
%(project_name)s

<h2>Step 1: Share</h2>

<h3>%(awesm_url)s</h3>

Welcome to KickBacker. Start sharing your link (%(awesm_url)s) immediately. Not only will you further the chances that <b>%(project_name)s</b> is funded, but you also could win the KickBack up for grabs. Share here: %(leaderboard)s and track how well you are doing compared to other KickBackers.

"""

templates = {

	'new_kb': { 'template_name': 'New Kickbacker',
				'template_values' : { 
										'body_content' : '',
									}
				 },
	'new_kb_user': { 'template_name': 'New Kickbacker User',
				'template_values' : { #  'awesm_link' : '',
									#	'leaderboard' : '',
									#	'left_column_image' : '',
									#	'right_column_image' : '',
									}
				 },
	'new_kb_project': { 'template_name': 'New Kickbacker Project',
				'template_values' : {   'awesm_link' : '',
										'leaderboard' : '', 
										'left_column_image' : '',
										'right_column_image' : '',
									}
				 },

}
