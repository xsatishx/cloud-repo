#
# Cookbook Name:: nova-neutron-pdc$
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

package "neutron-server" do
  action :install
end
package "neutron-plugin-ml2" do
  action :install
end


service "neutron-server" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

template "/etc/neutron/neutron.conf" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.cloud.chef_version}/#{ node.type }/neutron.conf.erb"
  notifies :restart, "service[neutron-server]"
  notifies :restart, "service[nova-scheduler]"
  notifies :restart, "service[nova-api]"
end
template "/etc/neutron/plugins/ml2/ml2_conf.ini" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.cloud.chef_version}/#{ node.type }/plugins/ml2/ml2_conf.ini.erb"
  variables(
  )
  notifies :restart, "service[neutron-server]"
end
template "/root/initialize_openstack/initialize_neutron.sh" do
  mode "400"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/#{ node.type }/initialize_neutron.sh.erb"
end
