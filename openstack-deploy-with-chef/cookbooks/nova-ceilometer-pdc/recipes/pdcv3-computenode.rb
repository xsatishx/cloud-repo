#
# Cookbook Name:: nova-ceilometer-pdc
# Recipe:: pdcv3
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#

package "ceilometer-agent-compute" do
  action :install
  action :upgrade
end
service "ceilometer-agent-compute" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]#, :start, :restart]
end
template "/etc/ceilometer/ceilometer.conf" do 
  mode "440"
  owner "ceilometer"
  group "ceilometer"
  source "#{node.cloud.chef_version}/ceilometer.conf.erb"
  notifies :restart, "service[ceilometer-agent-compute]"
end
