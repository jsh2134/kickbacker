import os

from fabric.api import env, settings
from fabric.api import sudo, run, local, put


HOSTS = {	
			'jeffdev' : {   'user': 'jhull',
							'host': 'office.buzzient.com:34343'
						  }	,

			'web1' : { 'user':'ec2-user',
						'host':'23.23.78.193', 
						'key': '/home/jhull/.ssh/jeffec2.pem'
			},
		}

env.key_filename = '/home/jhull/.ssh/jeffec2.pem'

def host(hostname):
	print type(hostname)
	env.hosts.append("%s@%s" % ( HOSTS[hostname]['user'], \
							HOSTS[hostname]['host']))

def ssh(host):
	local('ssh -i %s %s@%s' % ( HOSTS[host]['key'],
								HOSTS[host]['user'],
								HOSTS[host]['host'],
								) )

def deploy_web():

	# Create User
	user = 'kickbacker'
	home_dir = '/home/' + user 
	
	with settings(warn_only=True):
		sudo('useradd -U -m %s' % user)

	# Install packages with yum
	#sudo('yum install -y gcc')

	# Install pip
	sudo('curl -O http://pypi.python.org/packages/source/p/pip/pip-1.0.tar.gz')
	run('tar xvfz pip-1.0.tar.gz')
	sudo('cd pip-1.0 && python setup.py install')

	run('echo $PYTHONPATH')

	# Install virtualenv 
	sudo('pip install virtualenv')
	venv_name = '%s-env' % user
	venv = os.path.join(home_dir, venv_name)
	sudo('virtualenv --no-site-packages %s' % venv)

	run('echo $PYTHONPATH')

	# Activate Virtual Env
	#sudo('source %s/bin/activate' % venv)
	
	# Install python requirements
	put('requirements.txt', home_dir, use_sudo=True)
	sudo('%s/bin/pip install -r %s/requirements.txt' % (venv, home_dir))

	# Update python encoding
	pyv = run("""python -c 'import sys; print "%s.%s" % (sys.version_info[0], sys.version_info[1])""")
	sudo("""sed -i 's/encoding.[^!]*=.*\"ascii\"/encoding=\"utf8\"/' %s/lib/python%s/site.py""" % (venv, pyv) )



# Test Functions
################

def what_is_my_name():
	run('whoami')

def what_is_sudos_name():
	sudo('whoami')


