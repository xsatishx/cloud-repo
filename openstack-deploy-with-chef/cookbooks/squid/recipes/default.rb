#
# Cookbook Name:: hosts
# Recipe:: squid
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#

package "squid3" do
  action :install
end

service "squid3" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end

template "/etc/squid3/squid.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.chef_environment}/squid.conf.erb"
  action :create
  notifies :restart, "service[squid3]"
end
