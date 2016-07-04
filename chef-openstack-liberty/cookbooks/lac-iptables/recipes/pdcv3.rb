#
# Cookbook Name:: lac-iptables
# Recipe:: default
#
# Copyright 2013, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

# package iptables do
#  action :install
# end

webips=data_bag_item('firewall', 'empty')
oicrips=data_bag_item('firewall', 'oicrips')
cghubips=data_bag_item('firewall','pdccollaboratory')
wideips={}
wideips['ips']=oicrips['ips']+cghubips['ips']

targetnode = data_bag_item('yates', 'nodes')[node.name]
interfaces = []
%w(interfaces bonds bridges).each do |i|
  next unless targetnode.include? i
  interfaces += targetnode[i]
end
interfaces.collect!(&:strip)
interfaces.uniq!

@conf = '/etc/iptables.conf'
# This actually doesn't work, because
# it can't read this variable in the service blocks

template '/etc/iptables.conf' do
  # puts '------------------------------------------------------------------------------------------'
  # puts 'inside the pdcv3 recipe, this should run only if there was a change to the resulting file?'
  # puts '------------------------------------------------------------------------------------------'
  source "#{node.chef_environment}/iptables.conf.#{node.type}.erb"
  mode '755'
  owner 'root'
  group 'root'
  notifies :run, 'execute[iptablesrestore]', :immediately
  notifies :restart, 'service[nova-api-metadata]', :immediately
  notifies :restart, 'service[nova-network]', :immediately
  notifies :restart, 'service[nova-compute]', :immediately
  variables(interfaces: interfaces, webips: webips['ips'], wideips: wideips['ips'])
end

execute 'iptablesrestore' do
  # command('iptables-restore /etc/iptables.conf && echo /etc/iptables.conf > /tmp/thisreallydidexecute')
  # Simple sanity check ↑
  command('iptables-restore /etc/iptables.conf')
  action :nothing
end

service 'nova-network' do
  provider Chef::Provider::Service::Upstart
  supports status: true, restart: true, stop: true, start: true
  # action [:enable, :start, :restart]
  action :nothing
  only_if { File.exist? '/etc/init/nova-network.conf' }
end

service 'nova-compute' do
  provider Chef::Provider::Service::Upstart
  supports status: true, restart: true, stop: true, start: true
  # action [:enable, :start, :restart]
  action :nothing
  only_if { File.exist? '/etc/init/nova-compute.conf' }
end

service 'nova-api-metadata' do
  provider Chef::Provider::Service::Upstart
  supports status: true, restart: true, stop: true, start: true
  action :nothing
  only_if { File.exist? '/etc/init/nova-api-metadata.conf' }
end

cookbook_file '/root/flush_fw.sh' do
  source 'flush_fw.sh'
  mode 0500
  owner 'root'
  group 'root'
end
