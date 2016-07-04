#
# Cookbook Name:: nova-glance-pdc
# Recipe:: default
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
end

package "glance-api" do
  action :install
end

package "glance-client" do
  action :install
end

package "glance-common" do
  action :install
end

package "glance-registry" do
  action :install
end

service "glance-api" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

service "glance-registry" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

template "/etc/glance/glance-api-paste.ini" do 
  mode "440"
  owner "glance"
  group "glance"
  source "#{node.chef_environment}/glance-api-paste.ini.erb"
  variables(
  )
  notifies :restart, "service[glance-api]"
  notifies :restart, "service[glance-registry]"
end

template "/etc/glance/glance-registry.conf" do 
  mode "440"
  owner "glance"
  group "glance"
  source "#{node.chef_environment}/glance-registry.conf.erb"
  variables(
  )
  notifies :restart, "service[glance-api]"
  notifies :restart, "service[glance-registry]"
end
template "/etc/glance/glance-registry-paste.ini" do 
  mode "440"
  owner "glance"
  group "glance"
  source "#{node.chef_environment}/glance-registry-paste.ini.erb"
  variables(
  )
  notifies :restart, "service[glance-registry]"
  notifies :restart, "service[glance-api]"
end
template "/etc/glance/glance-api.conf" do 
  mode "440"
  owner "glance"
  group "glance"
  source "#{node.chef_environment}/glance-api.conf.erb"
  variables(
  )
  notifies :restart, "service[glance-registry]"
  notifies :restart, "service[glance-api]"
end
