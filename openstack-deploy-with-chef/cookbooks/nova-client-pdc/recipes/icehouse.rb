#
# Cookbook Name:: nova-client-pdc
# Recipe:: default
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#

package "nova-compute-kvm" do
  action :install
  action :upgrade
end
package "python-guestfs" do
  action :install
  action :upgrade
end
package "nova-network" do
  action :install
  action :upgrade
end
package "nova-api-metadata" do
  action :install
  action :upgrade
end


service "nova-compute" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start, :restart]
end
service "nova-network" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start, :restart]
end
service "nova-api-metadata" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start, :restart]
end

template "/etc/nova/nova.conf" do 
  mode "700"
  owner "nova"
  group "nova"
  source "#{node.chef_environment}/nova.conf.erb"
  variables(
        :chef_environment => "#{node.chef_environment}"
  )
  notifies :restart, "service[nova-compute]"
  notifies :restart, "service[nova-network]"
  notifies :restart, "service[nova-api-metadata]"
end

cookbook_file "/etc/kernel/postinst.d/statoverride" do
  source "#{node.chef_environment}/stateoverride"
  mode 0770
  owner "root"
  group "root"
  action :create
end

execute "statoverride" do
  command "dpkg-statoverride  --update --add root root 0644 /boot/vmlinuz-$(uname -r) || /bin/true"
  action :run
end
