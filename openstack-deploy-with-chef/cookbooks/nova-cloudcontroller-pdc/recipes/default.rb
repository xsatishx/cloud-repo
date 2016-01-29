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


package "nova-network" do
  action :install
end


package "nova-volume" do
  action :install
end

package "rabbitmq-server" do
  action :install
end


package "nova-consoleauth" do
  action :install
end


package "nova-cert" do
  action :install
end


package "nova-scheduler" do
  action :install
end


package "python-novaclient" do
  action :install
end


package "python-nova" do
  action :install
end


package "nova-vncproxy" do
  action :install
end


package "nova-doc" do
  action :install
end


package "nova-ajax-console-proxy" do
  action :install
end

template "/etc/nova/nova.conf" do 
  mode "440"
  owner "nova"
  group "nova"
  source "nova.conf.#{node.chef_environment}.erb"
 variables(
        :chef_environment => "#{node.chef_environment}"
  )
  #notifies :restart, "service[nova-compute]"
end

template "/etc/nova/api-paste.ini" do 
  mode "440"
  owner "nova"
  group "nova"
  source "api-paste.ini.#{node.chef_environment}.erb"
  variables(
        :chef_environment => "#{node.chef_environment}"
  )
  #notifies :restart, "service[nova-compute]"
end
