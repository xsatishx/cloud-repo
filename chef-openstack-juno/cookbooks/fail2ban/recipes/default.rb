#
# Cookbook Name:: hosts
# Recipe:: default
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#

package "fail2ban" do
  action :install
end

service "fail2ban" do
  provider Chef::Provider::Service::Init
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:restart, :start]
end

template "/etc/fail2ban/jail.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/jail.conf.erb"
  variables(
  )
  action :create
  notifies :restart, "service[fail2ban]"
end

template "/etc/fail2ban/jail.d/apache.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/jail.d/apache.conf.erb"
  action :create
  notifies :restart, "service[fail2ban]"
end

template "/etc/fail2ban/filter.d/apache-attackers.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/filter.d/apache-attackers.conf.erb"
  action :create
  notifies :restart, "service[fail2ban]"
end
template "/etc/fail2ban/jail.d/apache-attackers.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/jail.d/apache-attackers.conf.erb"
  notifies :restart, "service[fail2ban]"
end
template "/etc/fail2ban/filter.d/apache-dos.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/filter.d/apache-dos.conf.erb"
  action :create
  notifies :restart, "service[fail2ban]"
end
template "/etc/fail2ban/jail.d/apache-dos.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/jail.d/apache-dos.conf.erb"
  action :create
  notifies :restart, "service[fail2ban]"
end

remote_directory '/var/log/apache' do
  action :create_if_missing
  source "apache"
end
