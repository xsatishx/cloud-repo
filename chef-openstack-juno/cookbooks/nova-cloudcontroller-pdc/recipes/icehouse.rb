#
# Cookbook Name:: nova-cloudcontroller-pdc
# Recipe:: default
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#

package "nova-api" do
  action :install
end

package "nova-cert" do
  action :install
end

package "nova-conductor" do
  action :install
end

package "nova-consoleauth" do
  action :install
end


package "nova-novncproxy" do
  action :install
end

package "nova-scheduler" do
  action :install
end

package "python-novaclient" do
  action :install
end

service "nova-api" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

service "nova-cert" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

service "nova-consoleauth" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

service "nova-scheduler" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

service "nova-conductor" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

service "nova-novncproxy" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

template "/etc/nova/nova.conf" do 
  mode "440"
  owner "nova"
  group "nova"
  source "#{node.chef_environment}/nova.conf.erb"
  variables(
        :chef_environment => "#{node.chef_environment}"
  )
  notifies :restart, "service[nova-api]"
  notifies :restart, "service[nova-cert]"
  notifies :restart, "service[nova-consoleauth]"
  notifies :restart, "service[nova-scheduler]"
  notifies :restart, "service[nova-conductor]"
  notifies :restart, "service[nova-novncproxy]"
end

#template "/etc/nova/api-paste.ini" do 
#  mode "440"
#  owner "nova"
#  group "nova"
#  source "api-paste.ini.#{node.chef_environment}.erb"
#  variables(
#        :chef_environment => "#{node.chef_environment}"
#  )
#  #notifies :restart, "service[nova-compute]"
#end
