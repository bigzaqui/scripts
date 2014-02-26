#!/usr/bin/python
import MySQLdb
from subprocess import call
import logging
import time
import sys
import subprocess, threading
from contextlib import closing


logger = logging.getLogger('backup_raw')
hdlr = logging.FileHandler('/var/log/backup_raw.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

# db = MySQLdb.connect(host="localhost", # your host, usually localhost
#                      user="backup", # your username
#                      passwd="Aemae7Oh") # name of the data base

db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     passwd="password") # name of the data base
lock_sucess = True;
with closing( db.cursor() ) as cur:

	class Command(object):
	    def __init__(self):
	        self.process = None

	    def run(self, timeout):
	        def target():
				logger.info('locking tables')
				cur.execute("FLUSH TABLES WITH READ LOCK;")

	        thread = threading.Thread(target=target)
	        thread.start()

	        thread.join(timeout)
	        if thread.is_alive():
	            global lock_sucess
	            logger.warning("the thread was not able to lock the tables, finishing execution")
	            db.close()
	            lock_sucess = False


	command = Command()
	command.run(timeout=5)

	time.sleep(10) # sleep for 60 seconds, we will continue only if the thread was successful to apply the READ LOCK
	print ("sigo")
	if lock_sucess:
		logger.info('creating snapshot')
		#call(["lvcreate", "--size 50G --snapshot --name snap_database /dev/vinnie/database"])

		logger.info('unlocking tables')
		cur.execute("UNLOCK TABLES;")

		#Do the backup
		# logger.info('mounting snapshot')
		# call(["mount", "/dev/vinnie/snap_database /mnt/snapshot"])
		 

		# logger.info('running backup')
		# call(["rsync", "--omit-dir-times -a --no-o --no-g -vz --progress --delete /mnt/snapshot/ /mnt/backup/database/raw/"])


		# logger.info('unmounting snapshot')
		# call(["umount", "/mnt/snapshot"])

		# logger.info('delete snapshot')
		# call(["lvremove", "-f /dev/vinnie/snap_database"])

		logger.info('Backup finished')
	else:
		logger.warning('Backup finished with errors')
		sys.exit(-1)

db.close()
sys.exit(0)