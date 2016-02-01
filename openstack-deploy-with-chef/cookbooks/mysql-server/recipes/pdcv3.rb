#
# Cookbook Name:: mysql-server-5.5
# Recipe:: default
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#
#
package "mysql-server-5.5" do
  action :install
  #response_file "mysql-server-5.5.#{node.chef_environment}.seed"
  response_file "#{node.cloud.chef_version}/mysql-server-5.5.seed.erb"
  notifies :create, "template[/etc/mysql/conf.d/overrides.cnf]", :immediately
end

template "/etc/mysql/conf.d/overrides.cnf" do
  mode "440"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/mysql_overrides.cnf.erb"
  variables(
  )
  action :create
  notifies :restart , "service[mysql]", :immediately
end

service "mysql" do
  provider Chef::Provider::Service::Init::Debian
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

template "/root/.my.cnf" do
  mode "400"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/my.cnf.erb"
end

template "/etc/security/limits.d/mysql.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/limits.d/mysql.conf.erb"
end
