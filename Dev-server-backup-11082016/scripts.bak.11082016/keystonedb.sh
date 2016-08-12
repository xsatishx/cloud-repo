mysql -u root -phealthseq <<MYSQL_SCRIPT
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY 'healthseq';
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY 'healthseq';
MYSQL_SCRIPT
