#
# Cookbook Name:: nova-cinder-pdc
# Recipe:: default
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#

package "cinder-api" do
  action :install
  action :upgrade
end
package "cinder-scheduler" do
  action :install
  action :upgrade
end

service "cinder-api" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end
service "cinder-scheduler" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end

template "/etc/cinder/cinder.conf" do 
  mode "700"
  owner "cinder"
  group "cinder"
  source "#{node.cloud.chef_version}/cinder.conf.erb"
  notifies :restart, "service[cinder-api]"
  notifies :restart, "service[cinder-scheduler]"
end
template "/root/initialize_openstack/initialize_cinder.sh" do 
  mode "400"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/initialize_cinder.sh.erb"
end
