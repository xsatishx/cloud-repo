#
# Cookbook Name:: nova-ceilomter-pdc
# Recipe:: pdcv3
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#

package "ceilometer-api" do
  action :install
  action :upgrade
end
package "ceilometer-collector" do
  action :install
  action :upgrade
end
package "ceilometer-agent-central" do
  action :install
  action :upgrade
end
package "ceilometer-agent-notification" do
  action :install
  action :upgrade
end
package "ceilometer-alarm-evaluator" do
  action :install
  action :upgrade
end
package "ceilometer-alarm-notifier" do
  action :install
  action :upgrade
end
package "python-ceilometerclient" do
  action :install
  action :upgrade
end
package "mongodb-server" do
  action :install
  action :upgrade
end

service "ceilometer-agent-central" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable]#, :start, :restart]
  action [:enable]
end
service "ceilometer-agent-notification" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable]#, :start, :restart]
  action [:enable]
end
service "ceilometer-api" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]# :start, :restart]
end
service "ceilometer-collector" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]#, :start, :restart]
end
service "ceilometer-alarm-evaluator" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]#, :start, :restart]
end
service "ceilometer-alarm-notifier" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]#, :start, :restart]
end
service "mongodb" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]#, :start, :restart]
end

template "/etc/mongodb.conf" do 
  mode "440"
  owner "mongodb"
  group "mongodb"
  source "#{node.cloud.chef_version}/#{ node.type }/mongodb.conf.erb"
  notifies :restart, "service[mongodb]"
end
template "/etc/ceilometer/ceilometer.conf" do 
  mode "440"
  owner "ceilometer"
  group "ceilometer"
  source "#{node.cloud.chef_version}/ceilometer.conf.erb"
  notifies :restart, "service[ceilometer-agent-central]"
  notifies :restart, "service[ceilometer-agent-notification]"
  notifies :restart, "service[ceilometer-api]"
  notifies :restart, "service[ceilometer-collector]"
  notifies :restart, "service[ceilometer-alarm-evaluator]"
  notifies :restart, "service[ceilometer-alarm-notifier]"
end
template "/root/initialize_openstack/initialize_ceilometer.sh" do
  mode "400"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/#{ node.type }/initialize_ceilometer.sh.erb"
end
