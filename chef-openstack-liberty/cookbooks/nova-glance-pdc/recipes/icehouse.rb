#
# Cookbook Name:: nova-glance-pdc
# Recipe:: icehouse
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#
#


#NOTE: Need to precreate the mysql tables before chef-client is ran
#NOTE: Need to run two commands after the fact to init db

package "glance" do
  action :install
  action :upgrade
end

package "glance-api" do
  action :install
  action :upgrade
end

package "python-glanceclient" do
  action :install
  action :upgrade
end

package "glance-common" do
  action :install
  action :upgrade
end

package "glance-registry" do
  action :install
  action :upgrade
end

package "python-glance" do
  action :install
  action :upgrade
end

service "glance-api" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start, :restart]
end

service "glance-registry" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start, :restart]
end

template "/etc/glance/glance-api.conf" do 
  mode "440"
  owner "glance"
  group "glance"
  source "#{node.chef_environment}/glance-api.conf.erb"
  variables(
  )
  notifies :restart, "service[glance-api]"
end

template "/etc/glance/glance-registry.conf" do 
  mode "440"
  owner "glance"
  group "glance"
  source "#{node.chef_environment}/glance-registry.conf.erb"
  variables(
  )
  notifies :restart, "service[glance-registry]"
end
