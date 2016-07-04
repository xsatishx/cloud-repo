#
# Cookbook Name:: nova-cinder-pdc
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

##Stoage Nodes
package "smartmontools" do
  action :install
  action :upgrade
end
package "swift" do
  action :install
  action :upgrade
end
package "swift-account" do
  action :install
  action :upgrade
end
package "swift-container" do
  action :install
  action :upgrade
end
package "swift-object" do
  action :install
  action :upgrade
end
package "xfsprogs" do
  action :install
  action :upgrade
end 
package "rsync" do
  action :install
  action :upgrade
end 
service "swift-container" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-container-sync" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-container-replicator" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-container-updater" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-container-auditor" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-account" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-account-replicator" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-account-reaper" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-account-auditor" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-object" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-object-replicator" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-object-updater" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "swift-object-auditor" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "rsync" do
  provider Chef::Provider::Service::Init
  supports :status => true, :restart => true, :stop => true, :start => true
end

remote_directory "/root/install_scripts" do
	source "#{node.chef_environment}/install_scripts"
	owner "root"
	group "root"
	action :create


end

template  "/etc/swift/swift.conf"  do
  source "#{node.chef_environment}/swift.conf.erb"
  mode 0664
  owner "swift"
  group "swift"
  action :create
  notifies :restart, "service[swift-container]"
end
cookbook_file "/etc/default/rsync"  do
  source "#{node.chef_environment}/default/rsync"
  mode 0664
  owner "root"
  group "root"
  action :create
end
template "/etc/rsyncd.conf"  do
  source "#{node.chef_environment}/rsyncd.conf.erb"
  mode 0664
  owner "root"
  group "root"
  action :create
  notifies :restart, "service[rsync]"
end
template "/etc/swift/object-server.conf" do
  mode "700"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/object-server.conf.erb"
  notifies :restart, "service[swift-object]"
  notifies :restart, "service[swift-object-replicator]"
  notifies :restart, "service[swift-object-auditor]"
  notifies :restart, "service[swift-object-updater]"
end
template "/etc/swift/container-server.conf" do
  mode "700"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/container-server.conf.erb"
  notifies :restart, "service[swift-container]"
  notifies :restart, "service[swift-container-replicator]"
  notifies :restart, "service[swift-container-auditor]"
  notifies :restart, "service[swift-container-updater]"
  notifies :restart, "service[swift-container-sync]"
end
template "/etc/swift/account-server.conf" do
  mode "700"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/account-server.conf.erb"
  notifies :restart, "service[swift-account]"
  notifies :restart, "service[swift-account-replicator]"
  notifies :restart, "service[swift-account-auditor]"
  notifies :restart, "service[swift-account-reaper]"
end

cookbook_file "/etc/swift/account.builder" do
  mode "640"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/rings/account.builder"
end
cookbook_file "/etc/swift/container.builder" do
  mode "640"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/rings/container.builder"
end
cookbook_file "/etc/swift/object.builder" do
  mode "640"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/rings/object.builder"
end

