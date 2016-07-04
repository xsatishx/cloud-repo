#
# Cookbook Name:: yates
# Recipe:: iptables
#
# Copyright 2013, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

#package iptables do
#  action :install
#end

template "/etc/iptables.conf" do
  source "iptables/iptables.conf.#{node.chef_environment}.erb"
  mode "755"
  owner "root"
  group "root"
end
