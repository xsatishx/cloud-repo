#
# Cookbook Name:: nova-cinder-pdc
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

package "swift-proxy" do
  action :install
  action :upgrade
end
package "memcached" do
  action :install
  action :upgrade
end
package "python-keystoneclient" do
  action :install
  action :upgrade
end
package "python-swiftclient" do
  action :install
  action :upgrade
end
package "python-webob" do
  action :install
  action :upgrade
end

service "swift-proxy" do
  provider Chef::Provider::Service::Init::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable]
end
service "memcached" do
  provider Chef::Provider::Service::Init
  supports :status => true, :restart => true, :stop => true, :start => true
end

directory "/etc/swift/" do
  mode "770"
  owner "swift"
  group "swift"
end
directory "/etc/swift/keystone-signing" do
  mode "700"
  owner "swift"
  group "swift"
end
directory "/var/cache/swift" do
  mode "700"
  owner "swift"
  group "swift"
end


template "/etc/swift/proxy-server.conf" do 
  mode "700"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/proxy-server.conf.erb"
  notifies :restart, "service[swift-proxy]"
end

cookbook_file "/etc/swift/account.ring.gz" do 
  mode "640"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/rings/account.ring.gz"
  notifies :restart, "service[swift-proxy]"
end
cookbook_file "/etc/swift/container.ring.gz" do 
  mode "640"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/rings/container.ring.gz"
  notifies :restart, "service[swift-proxy]"
end
cookbook_file "/etc/swift/object.ring.gz" do 
  mode "640"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/rings/object.ring.gz"
  notifies :restart, "service[swift-proxy]"
end

cookbook_file "/etc/swift/swift-bionimbus-pdc.opensciencedatacloud.org.key" do
  mode "440"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/ssl/swift-bionimbus-pdc.opensciencedatacloud.org.key"
  notifies :restart, "service[swift-proxy]"
end
cookbook_file "/etc/swift/swift-bionimbus-pdc.opensciencedatacloud.org.crt" do
  mode "440"
  owner "swift"
  group "swift"
  source "#{node.chef_environment}/ssl/swift-bionimbus-pdc.opensciencedatacloud.org.crt"
  notifies :restart, "service[swift-proxy]"
end
