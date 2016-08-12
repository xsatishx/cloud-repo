mysql -u root -phealthseq <<MYSQL_SCRIPT 
CREATE DATABASE glance;
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' IDENTIFIED BY 'healthseq';
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' IDENTIFIED BY 'healthseq';
MYSQL_SCRIPT
