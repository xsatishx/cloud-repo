#
# Cookbook Name:: wordpress
# Recipe:: default
#
# # Maintainer Satish Balakrishnan <satish@healthseq.com>
#
# All rights reserved - Do Not Redistribute
#


# Install required packages
for packages in [ "apache2","curl","php-curl", "php-gd", "php-mbstring", "php-mcrypt", "php-xml", "php-xmlrpc", "mysql-client"] do
  package packages do
    action :install
  end
end

#download wordpress
remote_file "/tmp/latest.tar.gz" do
   source "https://wordpress.org/latest.tar.gz"
end

# untar
execute 'untar-wordpress' do
  command 'tar xzvf latest.tar.gz'
  cwd '/tmp'
  not_if { File.exists?("/tmp/wordpress/wp-config-sample.php") }
end

#copy wordpress dir to /var/www
bash 'copy-wordpress-www' do
  user 'root'
  cwd '/tmp'
  code <<-EOH
    cp -a wordpress/. /var/www/html
  EOH
end

# set permissions
bash 'chown-wordpress' do
  user 'root'
  code <<-EOH
    chown -R ubuntu:www-data /var/www/html
  
  EOH
end

# grab secure values from WordPress secret key generator and 
bash 'get-secret-key' do
  user 'root'
  cwd '/var/www/html/wordpress'
  code <<-EOH
    touch secret-key
    curl -s https://api.wordpress.org/secret-key/1.1/salt/ > secret-key
  EOH
 not_if { File.exists?("/var/www/html/wordpress/secret-key") }
end

# generate wp-config.php
bash 'get-secret-key' do
  user 'root'
  cwd '/var/www/html/wordpress'
  code <<-EOH
    cat /var/www/html/wordpress/secret-key  /tmp/main.yml> wp-config.php
  EOH
 not_if { File.exists?("/var/www/html/wordpress/wp-config.php") }
end

service "apache2" do
  action :restart
end