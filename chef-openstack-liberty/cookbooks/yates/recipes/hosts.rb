#
# Cookbook Name:: yates
# Recipe:: hosts
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

template "/etc/hosts" do
  mode "444"
  owner "root"
  group "root"
  source "hosts/hosts.#{node.chef_environment}.erb"
  variables(
  )
  action :create
end
