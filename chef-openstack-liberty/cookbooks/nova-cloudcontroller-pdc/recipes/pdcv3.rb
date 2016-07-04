#
# Cookbook Name:: nova-cloudcontroller-pdc
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

apt_repository 'openstack' do
  uri 'http://ubuntu-cloud.archive.canonical.com/ubuntu'
  components ['main']
  distribution "#{node.lsb.codename}-updates/#{node.nova.version}"
  action :add
end

package "nova-api" do
  action :install
end

package "nova-cert" do
  action :install
end

package "nova-conductor" do
  action :install
end

package "nova-consoleauth" do
  action :install
end


package "nova-novncproxy" do
  action :install
end

package "nova-scheduler" do
  action :install
end

package "python-novaclient" do
  action :install
end
package "rabbitmq-server" do
  action :install
end


service "nova-api" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end

service "nova-cert" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end

service "nova-consoleauth" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end

service "nova-scheduler" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end

service "nova-conductor" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end

service "nova-novncproxy" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end

template "/etc/nova/nova.conf" do 
  mode "440"
  owner "nova"
  group "nova"
  source "#{node.cloud.chef_version}/nova.conf.erb"
  notifies :restart, "service[nova-api]"
  notifies :restart, "service[nova-cert]"
  notifies :restart, "service[nova-consoleauth]"
  notifies :restart, "service[nova-scheduler]"
  notifies :restart, "service[nova-conductor]"
  notifies :restart, "service[nova-novncproxy]"
end

template "/root/initialize_openstack/initialize_nova.sh" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/initialize_nova.sh.erb"
end


template "/etc/security/limits.d/rabbitmq.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/limits.d/rabbitmq.conf.erb"
end
template "/etc/security/limits.d/nova.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/limits.d/nova.conf.erb"
end
template "/etc/security/limits.d/glance.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/limits.d/glance.conf.erb"
end
