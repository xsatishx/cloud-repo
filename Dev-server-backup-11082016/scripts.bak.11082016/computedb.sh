mysql -u root -phealthseq <<MYSQL_SCRIPT 
CREATE DATABASE nova;
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' IDENTIFIED BY 'healthseq';
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY 'healthseq';
MYSQL_SCRIPT
