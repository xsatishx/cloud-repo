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
package "neutron-plugin-ml2" do
  action :install
end
package "neutron-plugin-openvswitch-agent" do
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
service "neutron-dhcp-agent" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end
service "neutron-metadata-agent" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end
service "neutron-plugin-openvswitch-agent" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end
service "neutron-l3-agent" do
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
  notifies :restart, "service[neutron-dhcp-agent]"
  notifies :restart, "service[neutron-metadata-agent]"
  notifies :restart, "service[neutron-l3-agent]"
  notifies :restart, "service[neutron-plugin-openvswitch-agent]"
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
  notifies :restart, "service[neutron-server]"
  notifies :restart, "service[neutron-plugin-openvswitch-agent]"
end
template "/etc/neutron/l3_agent.ini" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.cloud.chef_version}/#{ node.type }/l3_agent.ini.erb"
  notifies :restart, "service[neutron-server]"
  notifies :restart, "service[neutron-plugin-openvswitch-agent]"
  notifies :restart, "service[neutron-l3-agent]"
end
template "/etc/neutron/dhcp_agent.ini" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.cloud.chef_version}/#{ node.type }/dhcp_agent.ini.erb"
  notifies :restart, "service[neutron-server]"
  notifies :restart, "service[neutron-dhcp-agent]"
end
template "/etc/neutron/metadata_agent.ini" do 
  mode "440"
  owner "neutron"
  group "neutron"
  source "#{node.cloud.chef_version}/#{ node.type }/metadata_agent.ini.erb"
  notifies :restart, "service[neutron-server]"
  notifies :restart, "service[neutron-metadata-agent]"
end
#template "/etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini" do 
#  mode "440"
#  owner "neutron"
#  group "neutron"
#  source "#{node.cloud.chef_version}/#{ node.type }//plugins/openvswitch/ovs_neutron_plugin.ini.erb"
#  variables(
#  )
#  notifies :restart, "service[neutron-server]"
#end
