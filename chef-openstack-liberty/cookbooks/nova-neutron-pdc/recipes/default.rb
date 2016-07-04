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
package "neutron-plugin-openvswitch" do
  action :install
end
package "neutron-plugin-openvswitch-agent" do
  action :install
end
package "openvswitch-datapath-dkms" do
  action :install
end
package "neutron-dhcp-agent" do
  action :install
end
package "neutron-l3-agent" do
  action :install
end




service "neutron-server" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end
service "openvswitch-switch" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

template "/etc/neutron/neutron.conf" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.chef_environment}/neutron.conf.erb"
  variables(
  )
  notifies :restart, "service[neutron-server]"
end
template "/etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.chef_environment}/plugins/openvswitch/ovs_neutron_plugin.ini.erb"
  variables(
  )
  notifies :restart, "service[neutron-server]"
end
template "/etc/neutron/plugins/ml2/ml2_conf.ini" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.chef_environment}/plugins/ml2/ml2_conf.ini.erb"
  variables(
  )
  notifies :restart, "service[neutron-server]"
end
template "/etc/sysctl.d/20.neutron.conf" do 
  mode "440"
  owner "root"
  group "root"
  source "#{node.chef_environment}/sysctl-neutron.conf.erb"
  variables(
  )
end
template "/etc/neutron/l3_agent.ini" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.chef_environment}/l3_agent.ini.erb"
  variables(
  )
end
template "/etc/neutron/dhcp_agent.ini" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.chef_environment}/dhcp_agent.ini.erb"
  variables(
  )
end
template "/etc/neutron/metadata_agent.ini" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.chef_environment}/metadata_agent.ini.erb"
  variables(
  )
end
