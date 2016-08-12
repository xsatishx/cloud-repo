mysql -u root -phealthseq <<MYSQL_SCRIPT
CREATE DATABASE cinder;
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' IDENTIFIED BY 'healthseq';
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' IDENTIFIED BY 'healthseq';
MYSQL_SCRIPT
