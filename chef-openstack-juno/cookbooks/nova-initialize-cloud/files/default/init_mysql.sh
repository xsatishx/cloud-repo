#Set password for mysql
source /root/creds_source

#Keystone
mysql -uroot -p$MYSQL_root_PASS -Dmysql -e"CREATE DATABASE keystone;"
mysql -uroot -p$MYSQL_root_PASS -Dmysql -e"GRANT ALL ON keystone.* TO 'keystone'@'%' IDENTIFIED BY '$MYSQL_keystone_PASS';"
mysql -uroot -p$MYSQL_root_PASS -Dmysql -e"GRANT ALL ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '$MYSQL_keystone_PASS';"
 
#SEtup mysql access for the glance user/service
mysql -uroot -p$MYSQL_root_PASS -Dmysql -e"CREATE DATABASE glance;"
mysql -uroot -p$MYSQL_root_PASS -Dmysql -e"GRANT ALL ON glance.* TO 'glance'@'%' IDENTIFIED BY '$MYSQL_glance_PASS';"
mysql -uroot -p$MYSQL_root_PASS -Dmysql -e"GRANT ALL ON glance.* TO 'glance'@'localhost' IDENTIFIED BY '$MYSQL_glance_PASS';"
 
#Nova
mysql -uroot -p$MYSQL_root_PASS -Dmysql -e"CREATE DATABASE nova;"
mysql -uroot -p$MYSQL_root_PASS -Dmysql -e"GRANT ALL ON nova.* TO 'nova'@'%' IDENTIFIED BY '$MYSQL_nova_PASS';"
mysql -uroot -p$MYSQL_root_PASS -Dmysql -e"GRANT ALL ON nova.* TO 'nova'@'localhost' IDENTIFIED BY '$MYSQL_nova_PASS';" 
