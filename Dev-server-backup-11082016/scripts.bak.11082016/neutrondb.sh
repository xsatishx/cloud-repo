mysql -u root -phealthseq <<MYSQL_SCRIPT 
CREATE DATABASE neutron;
GRANT ALL PRIVILEGES ON neutron.* TO neutron@'localhost' IDENTIFIED BY 'healthseq';
GRANT ALL PRIVILEGES ON neutron.* TO neutron@'%' IDENTIFIED BY 'healthseq';
MYSQL_SCRIPT
