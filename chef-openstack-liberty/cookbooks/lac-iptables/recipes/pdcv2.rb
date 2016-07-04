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

template "/etc/network/iptables.up.rules" do
  source "#{node.chef_environment}/iptables.up.rules.erb"
  mode "755"
  owner "root"
  group "root"
end
