import os

from fabric.api import env, settings
from fabric.api import sudo, lcd, cd, run, local, put

import ec2

from kickbacker import app
from deploy.amazon_settings import MAIN_IP, aws_defaults

USER_HOME = '/home/jhull/'
HOME_DIR = app.config['HOME']
TMP_PATH = '/tmp/'
S3CFG_FILE = '.s3cfg'
S3CFG_FP = os.path.join(HOME_DIR, 'deploy', S3CFG_FILE)
KB_BUCKET = 's3://kickbacker/'
HOSTS = {	
			'web1' : { 'user':'ec2-user',
						'host': MAIN_IP,
						'key': os.path.join(USER_HOME, '.ssh',\
								 aws_defaults['keypair']['file']),
						'dir': '/home/kickbacker/kickbacker-env',
						'env': '/home/kickbacker/kickbacker-env/bin/activate',
						'deploy_user': 'kickbacker',
			},
		}





env.key_filename = HOSTS['web1']['key']

def virtualenv(command, use_sudo=True):
	""" Execute a command with sudo under venv """
	with cd(env.directory):
		sudo('source ' + env.activate + ' && ' + command)#, user=env.deploy_user)
		


def host(hostname):
	print "Setting host to %s" % hostname
	env.host_string = "%s@%s" % ( HOSTS[hostname]['user'], \
									HOSTS[hostname]['host'])
	
	# Activate VirtualEnv
	if 'env' in HOSTS[hostname]:
		env.directory = HOSTS[hostname]['dir']
		env.activate = HOSTS[hostname]['env']
		env.deploy_user = HOSTS[hostname]['deploy_user']


def ssh(hostname):
	
	# Set Host
	host(hostname)

	local('ssh -i %s %s@%s' % ( HOSTS[hostname]['key'],
								HOSTS[hostname]['user'],
								HOSTS[hostname]['host'],
								) )


def deploy_web():

	# Create New Instance
	instance = ec2.create_new_instance()

	# Scrub past IP record from known_hosts
	local("ssh-keygen -R %s" % (instance.ip_address) )

	# Set Env Host String
	#env.host_string = "ec2-user@%s" % (instance.ip_address) 
	# In this case web1 is the host
	#TODO make this better
	host('web1')

	# Install Web
	install_web()

	return True


def install_web():

	# Create User
	user = 'kickbacker'
	remote_home_dir = '/home/' + user 
	
	with settings(warn_only=True):
		sudo('useradd -U -m %s' % user)
	
	remote_code_dir = os.path.join(remote_home_dir, 'kb')
	with settings(warn_only=True):
		sudo('mkdir %s' % remote_code_dir)

	# Install packages with yum
	sudo('yum install -y python-devel gcc nginx make')

	# Install s3cmd tools
	#install_s3cmd(remote_home_dir)

	# Install pip
	sudo('curl -O http://pypi.python.org/packages/source/p/pip/pip-1.0.tar.gz')
	run('tar xvfz pip-1.0.tar.gz')
	sudo('cd pip-1.0 && python setup.py install')

	# Install virtualenv 
	sudo('pip install virtualenv')
	venv_name = '%s-env' % user
	venv = os.path.join(remote_home_dir, venv_name)
	sudo('virtualenv --no-site-packages %s' % venv)

	# Activate Virtual Env
	virtualenv('source %s/bin/activate' % venv)
	
	# Install python requirements
	put('requirements.txt', remote_home_dir, use_sudo=True)
	virtualenv('pip install -r %s/requirements.txt' % (remote_home_dir))
	
	# Install Nginx Config
	put('nginx.conf', '/etc/nginx/nginx.conf', use_sudo=True)

	# Install Supervisor Config
	sudo('mkdir %s/etc/' % venv)
	sudo('mkdir /var/log/supervisord/')
	put('supervisord.conf', '%s/etc/supervisord.conf' % venv, use_sudo=True)

	# Update python encoding
	pyv = run("""python -c 'import sys; print "%s.%s" % (sys.version_info[0], sys.version_info[1])'""")
	sudo("""sed -i 's/encoding.[^!]*=.*\"ascii\"/encoding=\"utf8\"/' %s/lib/python%s/site.py""" % (venv, pyv) )

	# Make Kickbacker log
	sudo('touch /var/log/kickbacker.log')
	sudo('chown kickbacker:kickbacker /var/log/kickbacker.log')

	# Deploy Code
	update_code()

	# Install Redis
	install_redis()

	start_app()

def update_server():
	""" Update code on server """
	update_code()
	restart_app()

def start_app():
	# start nginx
	sudo('service nginx start')

	# start supervisor
	virtualenv('supervisord')

def restart_app():
	virtualenv('supervisorctl restart celery kickbacker')


def update_code():
	with lcd(HOME_DIR):
		local('git archive --format=tar.gz --output %s HEAD' % \
									os.path.join(TMP_PATH, 'app.tar.gz'))
	put( os.path.join(TMP_PATH,'app.tar.gz'), os.path.join(env.directory, 'app.tar.gz'), use_sudo=True)
	sudo('gunzip -f %s' % os.path.join(env.directory, 'app.tar.gz'))
	with cd(env.directory):
		sudo("find . -name '*.pyc' | xargs rm")
		sudo('tar -xvf %s' % os.path.join(env.directory, 'app.tar'))


def install_redis():

	with settings(warn_only=True):
		sudo('useradd redis', pty=True)
		sudo('mkdir %s' % os.path.join(os.path.sep, 'var','run','redis'), pty=True)
		sudo('mkdir %s' % os.path.join(os.path.sep, 'var','lib','redis'), pty=True)
		sudo('mkdir %s' % os.path.join(os.path.sep, 'var','log','redis'), pty=True)
		sudo('mkdir %s' % os.path.join(os.path.sep, 'etc','redis'), pty=True)
		sudo('chown redis:redis /var/log/redis /var/lib/redis /var/run/redis')

	put('redis/redis.conf', '/etc/redis/redis.conf', use_sudo=True)
	put('redis/redis.init', '/etc/rc.d/init.d/redis', use_sudo=True, mode=751)

	sudo('wget http://download.redis.io/redis-stable.tar.gz', pty=True)
	sudo('tar xvzf redis-stable.tar.gz', pty=True)
	with cd('redis-stable'):
		sudo('make', pty=True)
		sudo('make install', pty=True)
		sudo('cp src/redis-server /usr/local/bin/')
		sudo('cp src/redis-cli /usr/local/bin/')

	sudo('service redis start', pty=True)



