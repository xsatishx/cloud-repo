#
# Cookbook Name:: nova-keystone-pdc
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

package "python-keystoneclient" do
  action :install
end

package "python-mysqldb" do
  action :install
end

package "keystone" do
  action :install
end

service "keystone" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

template "/etc/keystone/keystone.conf" do 
  mode "440"
  owner "keystone"
  group "keystone"
  source "keystone.conf.#{node.chef_environment}.erb"
  variables(
  )
  notifies :restart, "service[keystone]"
end
