#!/usr/bin/python
#Created: 26 feb 2014 14:25:50 CET

import MySQLdb
import logging
import time
import sys
import subprocess, threading
import graypy
import commands

mysql_user="user"
mysql_password="password"


###############################################################################################
logger = logging.getLogger('backup_raw')
handler = graypy.GELFHandler('logging902.office.alatest.se', 12201, facility="sysadmin-backup-vinnie-raw")
hdlr = logging.FileHandler('/var/log/backup_raw.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.addHandler(handler) 
logger.setLevel(logging.INFO)
###############################################################################################

def create_db():
	global mysql_user
	global mysql_password
	db = MySQLdb.connect(host="localhost", user=mysql_user,passwd=mysql_password)
	return db

########################################################
########################################################
lock_sucess = True;
db = create_db()
cur = db.cursor()

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd

    def run(self, timeout):
        def target():
            global cur
            try:
            	cur.execute(self.cmd)
            	logger.info("read lock sucefully applied")
            except:
            	logger.error("thread: my connection to the DB was killed")

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            raise Exception
            thread.join()
try:
	logger.info("attempting to apply read lock")
	command = Command("flush tables with read lock")
	command.run(timeout=60)

except Exception as e:
	logger.error('the read lock couldnt be applied')
	newdb = create_db()
	newcur = newdb.cursor()
	newcur.execute("select concat('KILL ',id,';') from information_schema.processlist where user='"+mysql_user+"' and info='flush tables with read lock'")
	for row in newcur.fetchall() :
		newcur.execute(row[0]) 
	newdb.close()
	lock_sucess = False
	print e



time.sleep(80) # sleep for 80 seconds, we will continue only if the thread was successful to apply the READ LOCK
if lock_sucess:

	def run_command(cmd):
		
		status, output = commands.getstatusoutput(cmd)
		if status == 0:
			if output.strip(): logger.info(output)
		else:
			logger.warning("Error executing the command " + cmd)
			logger.error(output)
			sys.exit(-1)

	logger.info('creating snapshot')
	run_command("lvcreate --size 50G --snapshot --name snap_database /dev/vinnie/database")

	logger.info('unlocking tables')
	cur.execute("UNLOCK TABLES;")

	logger.info('mounting snapshot')
	run_command("mount /dev/vinnie/snap_database /mnt/snapshot")
	 
	logger.info('running backup')
	run_command("rsync --omit-dir-times -a --no-o --no-g -vz --progress --delete /mnt/snaps")

	logger.info('unmounting snapshot')
	run_command("umount /mnt/snapshot")

	logger.info('delete snapshot')
	run_command("lvremove -f /dev/vinnie/snap_database")

	logger.info('Backup finished')
else:
	logger.warning('Backup finished with errors')
	sys.exit(-1)


sys.exit(0)