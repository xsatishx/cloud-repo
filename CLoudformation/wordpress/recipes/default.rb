#
# Cookbook Name:: wordpress
# Recipe:: default
#
# # Maintainer Satish Balakrishnan <satish@healthseq.com>
#
# All rights reserved - Do Not Redistribute
#


# Install required packages
for packages in [ "apache2","curl","php-curl", "php-gd", "php-mbstring", "php-mcrypt", "php-xml", "php-xmlrpc", "mysql-client", "libapache2-mod-php", "php7.0-mysql"] do
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
    cp -a wordpress/. /var/www/html/wordpress
  EOH
end

# set permissions
bash 'chown-wordpress' do
  user 'root'
  code <<-EOH
    chown -R ubuntu:www-data /var/www/html/wordpress
  
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
bash 'generate-config' do
  user 'root'
  cwd '/var/www/html/wordpress'
  code <<-EOH
    echo "<?php \n">> wp-config.php
    cat /var/www/html/wordpress/secret-key   >> wp-config.php
    cat /tmp/main.yml >> wp-config.php
    cat /home/ubuntu/cloudformation/wordpress/ender >> wp-config.php  
  EOH
 not_if { File.exists?("/var/www/html/wordpress/wp-config.php") }
end

# set perms
bash 'set perm' do
  user 'root'
  cwd '/var/www/html/wordpress'
  code <<-EOH
    chown -R www-data:www-data /var/www/html/wordpress/
    chmod -R 755 /var/www/html/wordpress/

  EOH
end

service "apache2" do
  action :restart
end



