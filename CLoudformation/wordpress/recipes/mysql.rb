#
# Cookbook Name:: wordpress
# Recipe:: mysql
#
# # Maintainer Satish Balakrishnan <satish@healthseq.com>
#
# All rights reserved - Do Not Redistribute
#




package 'python-pymysql' do
  action :install
  action :upgrade
end

package 'python-mysqldb' do
  action :install
  action :upgrade
end

cookbook_file '/tmp/generate.pl' do
  source 'generate.pl'
  owner 'root'
  group 'root'
  mode '0755'
  action :create
end

package "mysql-server" do
  action :install
  response_file 'mysql_seed'
end

template '/etc/mysql/mysql.conf.d/mysqld.cnf' do
  source 'mysqld.cnf.erb'
  owner 'root'
  group 'root'
  mode '0644'
end

bash 'generate-createdb-script' do
  user 'root'
  cwd '/tmp'
  code <<-EOH
    perl generate.pl
  EOH
end

bash 'Create-all-database' do
  user 'root'
  cwd '/tmp'
  code <<-EOH
    chmod a+x createdb.sh
    sh createdb.sh
  EOH
end

service "mysql" do
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:restart]
end