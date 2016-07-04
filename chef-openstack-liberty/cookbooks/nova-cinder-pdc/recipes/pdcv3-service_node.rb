#
# Cookbook Name:: nova-cinder-pdc
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

#package "lvm2" do
#  action :install
#  action :upgrade
#end
package "cinder-volume" do
  action :install
  action :upgrade
end
package "tgt" do
  action :install
  action :upgrade
end
package "python-mysqldb" do
  action :install
  action :upgrade
end

service "cinder-volume" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end
service "tgt" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end

#cookbook_file "/etc/lvm/lvm.conf"  do
#  source "#{node.chef_environment}/lvm.conf"
#  mode 0664
#  owner "root"
#  group "root"
#  action :create
#end

#cookbook_file "/root/create_partitions.sh"  do
#  source "#{node.chef_environment}/create_partitions.sh"
#  mode 0664
#  owner "root"
#  group "root"
#  action :create
#end

template "/etc/cinder/cinder.conf" do 
  mode "700"
  owner "cinder"
  group "cinder"
  source "#{node.cloud.chef_version}/cinder.conf.erb"
  notifies :restart, "service[cinder-volume]"
  notifies :restart, "service[tgt]"
end
