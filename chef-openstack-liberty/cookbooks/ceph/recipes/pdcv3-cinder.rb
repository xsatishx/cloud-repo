#
# Cookbook Name:: nova-ceph
# Recipe:: pdcv3
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

# #Ceph is currently deployed manually
## with ceph-deploy.  This pushes out
## its own ceph.conf
## Cinder nodes are currently
## living on the ceph osds
# package "python-ceph" do
#  action :install
#  action :upgrade
# end
directory '/etc/ceph' do
  action :create
  mode 0750
  owner 'ceph'
  group 'ceph'
end

user 'ceph' do
  action :create
  home '/home/ceph'
  shell '/bin/false'
  system true
end

#group 'ceph' do
#  action :manage
#  append true
#  members %w(nova cinder)
#end

unless node.tags.include? 'noceph'
  template '/etc/ceph/ceph.conf' do
    mode '440'
    owner 'ceph'
    group 'ceph'
    source "#{node.cloud.chef_version}/#{node.chef_environment}/ceph.conf.erb"
  end
  template '/etc/ceph/ceph.client.cinder.keyring' do
    mode '440'
    owner 'ceph'
    group 'ceph'
    source "#{node.cloud.chef_version}/#{node.chef_environment}/ceph.client.cinder.keyring.erb"
  end
  template '/etc/ceph/ceph.client.cinder.key' do
    mode '440'
    owner 'ceph'
    group 'ceph'
    source "#{node.cloud.chef_version}/#{node.chef_environment}/ceph.client.cinder.key.erb"
  end
end
