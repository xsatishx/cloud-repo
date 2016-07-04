#
# Cookbook Name:: nova-client-pdc
# Recipe:: default
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#

package "nova-compute-kvm" do
  action :install
end

service "nova-compute" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

template "/etc/nova/nova.conf" do 
  mode "700"
  owner "nova"
  group "nova"
  source "nova.conf.#{node.chef_environment}.erb"
  variables(
        :chef_environment => "#{node.chef_environment}"
  )
  notifies :restart, "service[nova-compute]"
end

template "/etc/nova/api-paste.ini" do 
  mode "700"
  owner "nova"
  group "nova"
  source "api-paste.ini.#{node.chef_environment}.erb"
  variables(
        :chef_environment => "#{node.chef_environment}"
  )
  notifies :restart, "service[nova-compute]"
end
