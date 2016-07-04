#
# Cookbook Name:: dnsmasq$
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

package "dnsmasq" do
  action :install
end

service "dnsmasq" do
  provider Chef::Provider::Service::Init
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:start, :restart ]
end

template "/etc/dnsmasq.conf" do 
  mode "440"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/dnsmasq.conf.erb"
  notifies :restart, "service[dnsmasq]"
end
template "/etc/resolv.conf.dnsmasq" do 
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/resolv.conf.dnsmasq.erb"
  notifies :restart, "service[dnsmasq]"
end
template "/etc/default/dnsmasq" do 
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/default_dnsmasq.erb"
  notifies :restart, "service[dnsmasq]"
end
