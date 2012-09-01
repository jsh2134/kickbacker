MAIN_IP = '23.23.215.239'

aws_defaults = { 'security' : ['sg1'],
			'ami' : 'ami-aecd60c7',
			'size':  't1.micro',
			'keypair' : { 
							'name': 'kp1',
							'file' : 'kp1.pem'
			  }
		 }

