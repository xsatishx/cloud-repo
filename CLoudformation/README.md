Readme 

1) cf-RDS
Description : Cloudformation script that installs two ec2 instances and an RDS instance. Chef is used to install and configure apache and wordpress.
Sets up a load balancer.

2) cf-mysql
Description : Cloudformation script that installs three ec2 instances. Two of them are used as webservers and the third one has mySQL database setup via Chef.
Chef is also used to install wordpress. Sets up a load balancer


Steps for  cf-RDS

Input: vpcid, instancetype, keyname, sshlocation ,dbname, dbuser, dbpassword

1) Creates 2 ec2 instances
2) Installs chef
3) Downloads wordpress chef repo 
4) saves the input data ie) dbname, dbuserm dbpassword and dbhost to a text file on the server. Dbhost is obtained via 'GetAtt' (main.yml)
5) Runs chef-solo to set up the components
	  - Installs php and apache
	  - Download wordpress setup file 
	  - gets the secret key from wordpress web api
	  - generates the wordpress wp-config file by combining the secret key and the  input data from step 4.
6) Setups up a AWS RDS DB instance using dbuser, dbpassword and dbname.	  
7) Sets up an load balancer with the above 2 ec2 instances.
	  

Steps for  cf-mysql

input: vpcid, instancetype, keyname, sshlocation, dbname, dbuser, dbrootpassword, dbpassword

1) Creates 2 ec2 instances to be used as webservers
2) intalls chef
3) Download wordpress chef repo
4) saves the input data ie) dbname, dbuserm dbpassword and dbhost to a text file on the server. Dbhost is obtained via 'GetAtt' (main.yml)
5) Runs chef-solo to set up the components on the webservers
	  - Installs php and apache
	  - Download wordpress setup file 
	  - gets the secret key from wordpress web api
	  - generates the wordpress wp-config file by combining the secret key and main.yml.
5) Creates an ec2instance to be used as the db server
6) installs chef
7) Downloads wordpress chef repo
8) saves mysql related input data to a file on the dbserver (creds)	  
9) Runs chef-solo to set up the components on the db server
	- installs mysql server and related packages
	- runs a perl script that uses creds file and creates a bash script to setup the database for wordpress using main.yml
	- runs the bash script to create the wordpress database