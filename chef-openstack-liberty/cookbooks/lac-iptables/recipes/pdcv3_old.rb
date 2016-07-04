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

@conf = '/etc/iptables.conf'
@updated = false

template @conf do
  source "#{node.chef_environment}/iptables.conf.#{ node.type }.erb"
  mode '755'
  owner 'root'
  group 'root'

  @updated = true

  #  notifies :restart, "service[nova-network]"
end

execute "iptables-restore #{@conf}" do
  # puts("iptables-restore #{@conf}")
  only_if @updated
  command("iptables-restore #{@conf}")
end

service 'nova-network' do
  provider Chef::Provider::Service::Upstart
  supports status: true, restart: true, stop: true, start: true
  action [:enable, :start, :restart]
  only_if { File.exist? '/etc/init/nova-network.conf' }
end

cookbook_file '/root/flush_fw.sh' do
  source 'flush_fw.sh'
  mode 0500
  owner 'root'
  group 'root'
end
