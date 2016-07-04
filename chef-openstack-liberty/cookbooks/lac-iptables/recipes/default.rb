#
# Cookbook Name:: lac-iptables
# Recipe:: default
#
# Copyright 2013, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

#package iptables do
#  action :install
#end

@conf="/etc/iptables.conf"

template @conf do
  source "iptables.conf.#{node.chef_environment}.erb"
  mode "755"
  owner "root"
  group "root"
end

execute "iptables-restore #{@conf}" do
  command("iptables-restore #{@conf}")
end

service "nova-network" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start, :restart]
  only_if{File.exists?"/etc/init/nova-network.conf"}
end
