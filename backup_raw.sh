#we use this way to send the commands whe can keep the read lock 
exec 3> >(mysql -u backup --password=password)

#set read lock
echo "FLUSH TABLES WITH READ LOCK;" >&3  

sleep 60
#create snapshot
lvcreate --size 50G --snapshot --name snap_database /dev/server/database 

#remove the READ LOCK
echo "UNLOCK TABLES;" >&3  

#kill the file descriptor
exec 3>&-

#Do the backup
mount /dev/server/snap_database /mnt/snapshot

#Do the backup, at low I/O and CPU priority
rsync -avz --progress --delete /mnt/snapshot/ /mnt/backup/database/raw/

#remove snapshot
umount /mnt/snapshot

#delete snapshot
lvremove -f /dev/server/snap_database

