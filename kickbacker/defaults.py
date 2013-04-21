import datetime

BACKER = { 	'name': '',
			'image' : 'http://d297h9he240fqh.cloudfront.net/cache-a733f566c/images/users/missing_small.png',
			'location' : '',
			'bio': '' ,
		}

PROJECT = { 'author' : '',
			'author_link': '',
			'desc': '',
			'desc_full': '',
			'started': '',
			'end': '',
			'img': '',
			'video': '',
			'loc': '',
			'backers_count': '',
			'goal': '',
			'pct-funded': '',
			'status': '',
			'funded': '',
			'amount': '',
			'end_time': '',
			'hours_left': '',
			'prizes': [],
	
}

# Create fake backers for non existent
FAKE_BACKERS = [
					{ 'name': 'Jim Clunrey',
					  'backer_type' :'sample',
					  'img' : '/static/img/sample-kb-1.jpg',
					  'key' : {  'created' : datetime.datetime.now() - datetime.timedelta(days=12),
								'clicks' : '0',
								'id' : '1',
								'rewards' : ['twitter',
											'facebook',],
							 }
					  },
					{ 'name': 'Joan Sylvia',
					  'backer_type' :'sample',
					  'img' : '/static/img/sample-kb-2.jpg',
					  'key' : {  'created' : datetime.datetime.now() - datetime.timedelta(days=22),
								'clicks' : '0',
								'id' : '2',
								'rewards' : ['youtube',
											],
							 }
					  },
					{ 'name': 'Matthew Morello',
					  'backer_type' :'sample',
					  'img' : '/static/img/sample-kb-3.jpg',
					  'key' : {  'created' : datetime.datetime.now() - datetime.timedelta(days=2),
								'clicks' : '0',
								'id' : '2',
								'rewards' : [],
							 }
					  },
					{ 'name': 'Lucia Mariana',
					  'backer_type' :'sample',
					  'img' : '/static/img/sample-kb-4.jpg',
					  'key' : {  'created' : datetime.datetime.now() - datetime.timedelta(days=2),
								'clicks' : '0',
								'id' : '2',
								'rewards' : [],
							 }
					  },
					{ 'name': 'Tuan Shinto',
					  'backer_type' :'sample',
					  'img' : '/static/img/sample-kb-5.jpg',
					  'key' : {  'created' : datetime.datetime.now() - datetime.timedelta(days=2),
								'clicks' : '0',
								'id' : '2',
								'rewards' : ['twitter'],
							 }
					  },
							  

]

