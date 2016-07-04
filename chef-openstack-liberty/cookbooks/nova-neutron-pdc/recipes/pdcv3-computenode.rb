#
# Cookbook Name:: nova-neutron-pdc$
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

package "neutron-common" do
  action :install
end
package "neutron-plugin-openvswitch-agent" do
  action :install
end
package "neutron-plugin-ml2" do
  action :install
end

service "neutron-plugin-openvswitch-agent" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

template "/etc/neutron/neutron.conf" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.cloud.chef_version}/#{ node.type }/neutron.conf.erb"
  notifies :restart, "service[neutron-plugin-openvswitch-agent]"
  notifies :restart, "service[nova-compute]"
end
template "/etc/sysctl.d/20.neutron.conf" do 
  mode "440"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/#{ node.type }/sysctl-neutron.conf.erb"
end
template "/etc/neutron/plugins/ml2/ml2_conf.ini" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.cloud.chef_version}/#{ node.type }/plugins/ml2/ml2_conf.ini.erb"
  notifies :restart, "service[neutron-plugin-openvswitch-agent]"
end

