#!/usr/bin/python
import MySQLdb
import logging
import time
import sys
import subprocess, threading

logger = logging.getLogger('backup_raw')
hdlr = logging.FileHandler('/var/log/backup_raw.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

def create_db():
	db = MySQLdb.connect(host="localhost", user="root",passwd="password")
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
	command.run(timeout=5)

except Exception as e:
	logger.error('the read lock couldnt be applied')
	newdb = create_db()
	newcur = newdb.cursor()
	newcur.execute("select concat('KILL ',id,';') from information_schema.processlist where user='root' and info='flush tables with read lock'")
	for row in newcur.fetchall() :
		newcur.execute(row[0]) 
	newdb.close()
	lock_sucess = False
	print e



time.sleep(10) # sleep for 60 seconds, we will continue only if the thread was successful to apply the READ LOCK
if lock_sucess:
	logger.info('creating snapshot')
	call(["lvcreate", "--size 50G --snapshot --name snap_database /dev/vinnie/database"])

	logger.info('unlocking tables')
	cur.execute("UNLOCK TABLES;")

	logger.info('mounting snapshot')
	call(["mount", "/dev/vinnie/snap_database /mnt/snapshot"])
	 
	logger.info('running backup')
	call(["rsync", "--omit-dir-times -a --no-o --no-g -vz --progress --delete /mnt/snapshot/ /mnt/backup/database/raw/"])

	logger.info('unmounting snapshot')
	call(["umount", "/mnt/snapshot"])

	logger.info('delete snapshot')
	call(["lvremove", "-f /dev/vinnie/snap_database"])

	logger.info('Backup finished')
else:
	logger.warning('Backup finished with errors')
	sys.exit(-1)


sys.exit(0)