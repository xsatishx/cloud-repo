#
# Cookbook Name:: hosts
# Recipe:: squid
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

@whitelists = %w(ftp_whitelist web_whitelist web_wildcard_whitelist)

package 'squid3' do
  action :install
end

service 'squid3' do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  # action [:enable, :start, :restart]
  action [:enable]
end

template '/etc/squid3/squid.conf' do
  mode '444'
  owner 'root'
  group 'root'
  source "#{node.chef_environment}/squid.conf.erb"
  action :create
  notifies :restart, 'service[squid3]'
end

# rulesets = data_bag_item("firewall", "proxy_whitelist")
#
# if rulesets.include?node.chef_environment
template '/etc/squid3/squid.conf.foo' do
  # variables({:ruleset=>rulesets[node.chef_environment]})
  mode '444'
  owner 'root'
  group 'root'
  source 'newsquid.conf.erb'
  action :create
end
# else
#  puts "No rules listed for #{node.chef_environment}, skipping"
# end

@whitelists.each do |whitelist|
  @whitelists -= [whitelist]
  cookbook_file "/etc/squid3/#{whitelist}" do
    mode '644'
    owner 'root'
    group 'root'
    source "#{node.chef_environment}/#{whitelist}"
    notifies :restart, 'service[squid3]'
  end
end

# @whitelists.each do |whitelist|
#  cookbook_file "/etc/squid3/#{whitelist}" do
#    mode '644'
#    owner 'root'
#    group 'root'
#    source whitelist
#  end
# end
