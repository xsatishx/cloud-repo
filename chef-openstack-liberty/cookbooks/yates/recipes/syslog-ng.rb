#
# Cookbook Name:: yates
# Recipe:: syslog-ng
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

package "syslog-ng" do
  action :install
end

service "syslog-ng" do
  provider Chef::Provider::Service::Init::Debian
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

template "/etc/syslog-ng/conf.d/01-remote.conf" do 
  mode "640"
  owner "root"
  group "root"
  source "syslog-ng/01-remote.conf.#{node.chef_environment}.erb"
  variables(
  )
  notifies :restart, "service[syslog-ng]"
end

template "/etc/ssl/private/syslog.norc.opensciencedatacloud.org.key" do 
  mode "700"
  owner "root"
  group "root"
  source "syslog-ng/syslog.#{node.chef_environment}.opensciencedatacloud.org.crt.erb"
  variables(
  )
  notifies :restart, "service[syslog-ng]"
end

template "/etc/ssl/certs/syslog.norc.opensciencedatacloud.org.crt" do 
  mode "700"
  owner "root"
  group "root"
  source "syslog-ng/syslog.#{node.chef_environment}.opensciencedatacloud.org.key.erb"
  variables(
  )
  notifies :restart, "service[syslog-ng]"
end
