#
# Cookbook Name:: hosts
# Recipe:: default
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#

template "/etc/hosts" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.chef_environment}/hosts.erb"
  variables(
  )
  action :create
end

