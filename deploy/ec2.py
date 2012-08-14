from boto.ec2.connection import EC2Connection
from secrets import AWS

import sys
import time

MAIN_IP = '23.23.78.193'
MAIN_SG = 'kp1'
MAIN_KP = 'jeffec2'

SERVER_TYPES = {
			'web' : {
						'image_id' : 'ami-aecd60c7',
						'instance_type' : 't1.micro',
						'security_groups' : [MAIN_SG],
						'key_name' : MAIN_KP,
				},
}


class EC2Conn:

	def __init__(self):
		self.conn = None


	def connect(self):
		self.conn = EC2Connection(AWS['access_key'],
								  AWS['secret_key'])

	def create_instance(self, instance_type='web', address=None):
		reservation = self.conn.run_instances( **SERVER_TYPES[instance_type])
		print reservation
		instance = reservation.instances[0]
		time.sleep(10)
		while instance.state != 'running':
			time.sleep(5)
			instance.update()
			print "Instance state: %s" % (instance.state)
		
		print "instance %s done!" % (instance.id)

		if address:	
			success = self.link_instance_and_ip(instance.id, address)
			if success:
				print "Linked %s to %s" % (instance.id, address)
			else:
				print "Falied to link%s to %s" % (instance.id, address)
			instance.update()

		return instance

	def link_instance_and_ip(self, instance_id, ip=MAIN_IP):
		success = self.conn.associate_address(instance_id=instance_id,
									public_ip=ip)
		if success: 
			print "Sleeing for 60 seconds to let IP attach"
			time.sleep(60)

		return success

	def unlink_instance_and_ip(self, instance_id, ip=MAIN_IP):
		return self.conn.disassociate_address(instance_id=instance_id,
									public_ip=ip)

	def get_instances(self):
		return self.conn.get_all_instances()


def create_new_instance(address=MAIN_IP):
	a = EC2Conn()
	a.connect()
	return a.create_instance(address=address)


if __name__ == '__main__':
	create_new_instance()


