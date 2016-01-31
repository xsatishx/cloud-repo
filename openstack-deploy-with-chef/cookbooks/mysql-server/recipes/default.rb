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
  response_file "mysql-server-5.5.seed.#{node.chef_environment}.erb"
  notifies :create, "template[/etc/mysql/conf.d/overrides.cnf]", :immediately
end

template "/etc/mysql/conf.d/overrides.cnf" do
  mode "440"
  owner "root"
  group "root"
  source "mysql_overrides.cnf.#{node.chef_environment}.erb"
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

