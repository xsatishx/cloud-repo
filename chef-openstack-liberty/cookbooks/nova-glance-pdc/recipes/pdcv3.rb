#
# Cookbook Name:: nova-glance-pdc
# Recipe:: icehouse
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#
#


package "glance" do
  action :install
  action :upgrade
end

package "glance-api" do
  action :install
  action :upgrade
end

package "python-glanceclient" do
  action :install
  action :upgrade
end

package "glance-common" do
  action :install
  action :upgrade
end

package "glance-registry" do
  action :install
  action :upgrade
end

package "python-glance" do
  action :install
  action :upgrade
end

service "glance-api" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end

service "glance-registry" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [:enable, :start, :restart]
  action [:enable]
end

template "/etc/glance/glance-registry.conf" do 
  mode "440"
  owner "glance"
  group "glance"
  source "#{node.cloud.chef_version}/glance-registry.conf.erb"
  variables(
  )
  notifies :restart, "service[glance-registry]"
end

template "/root/initialize_openstack/initialize_glance.sh" do
  mode "400"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/initialize_glance.sh.erb"
end

glancetarget=nil
if node.attributes.include?"glancetarget"
  if node.attributes["glancetarget"]=="ceph"
    glancetarget="ceph"
  elsif node.attributes["glancetarget"]=="local"
    glancetarget="local"
  else
    puts "No reasonable (ceph|local) glancetarget defined, assuming ceph since that was the old default"
    glancetarget="ceph"
  end
else
  puts "No glancetarget defined, assuming ceph since that was the old default"
  glancetarget="ceph"
end

template "/etc/glance/glance-api.conf" do 
  mode "440"
  owner "glance"
  group "glance"
  source "#{node.cloud.chef_version}/glance-#{glancetarget}-api.conf.erb"
  variables(
  )
  notifies :restart, "service[glance-api]"
end
