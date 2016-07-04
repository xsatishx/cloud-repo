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
end

execute 'iptablesrestore' do
  # command('iptables-restore /etc/iptables.conf && echo /etc/iptables.conf > /tmp/thisreallydidexecute')
  # Simple sanity check ↑
  command('iptables-restore /etc/iptables.conf')
  action :nothing
end

cookbook_file '/root/flush_fw.sh' do
  source 'flush_fw.sh'
  mode 0500
  owner 'root'
  group 'root'
end
