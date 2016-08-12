mysql -u root -phealthseq <<MYSQL_SCRIPT
CREATE DATABASE heat;
GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'localhost' IDENTIFIED BY 'healthseq';
GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'%' IDENTIFIED BY 'healthseq';
MYSQL_SCRIPT

