#
# Cookbook Name:: cpu
# Recipe:: pdcv3
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

package "cpu" do
  action :install
  action :upgrade
end
template "/etc/cpu/cpu.conf" do 
  mode "440"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/cpu.conf.erb"
end


