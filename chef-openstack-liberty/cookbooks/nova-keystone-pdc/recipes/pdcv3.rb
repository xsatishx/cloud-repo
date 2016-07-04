#
# Cookbook Name:: nova-keystone-pdc
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

package "python-keystoneclient" do
  action :install
end

package "python-mysqldb" do
  action :install
end

package "keystone" do
  action :install
end

service "keystone" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

template "/etc/keystone/keystone.conf" do 
  mode "440"
  owner "keystone"
  group "keystone"
  source "#{node.cloud.chef_version}/keystone.conf.erb"
  variables(
  )
  notifies :restart, "service[keystone]"
end

template "/etc/keystone/keystone-paste.ini" do 
  mode "440"
  owner "keystone"
  group "keystone"
  source "#{node.cloud.chef_version}/keystone-paste.ini.erb"
  variables(
  )
  notifies :restart, "service[keystone]"
end

directory "/root/initialize_openstack" do
  mode "700"
  owner "root"
  group "root"
end

template "/root/initialize_openstack/initialize_keystone.sh" do
  mode "400"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/initialize_keystone.sh.erb"
end

template "/root/initialize_openstack/initialize_rabbitmq.sh" do
  mode "400"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/initialize_rabbitmq.sh.erb"
end
template "/root/initialize_openstack/initialize_mysql.sh" do
  mode "400"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/initialize_mysql.sh.erb"
end

template "/etc/cron.daily/flush_tokens" do
  mode "500"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/flush_tokens.sh.erb"
end

file "/etc/keystone/ssl.ca-bundle" do
  content "#{node.ssl.ca_bundle}"
  owner "keystone"
  group "keystone"
  mode "0440"
end
file "/etc/keystone/ssl.crt" do
  content "#{node.ssl.wildcard_cert}"
  owner "keystone"
  group "keystone"
  mode "0440"
end
file "/etc/keystone/ssl.key" do
  content "#{node.ssl.wildcard_key}"
  owner "keystone"
  group "keystone"
  mode "0440"
end



