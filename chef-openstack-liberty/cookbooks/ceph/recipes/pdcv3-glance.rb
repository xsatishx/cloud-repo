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
## All this does is make sure we're using the right repo

apt_repository 'ceph' do
  uri "http://ceph.com/debian-#{node.ceph.release_name}/"
  components ['main']
  distribution node.lsb.codename
  key 'https://git.ceph.com/git/?p=ceph.git;a=blob_plain;f=keys/release.asc'
  action :add
end


## Cinder nodes are currently
## living on the ceph osds

#unless node.tags.include? 'noceph'
#  package 'python-ceph' do
#    action :install
#    action :upgrade
#  end
#  directory '/etc/ceph' do
#    action :create
#    mode 0750
#    owner 'ceph'
#    group 'ceph'
#  end
#
#  user 'ceph' do
#    action :create
#    home '/home/ceph'
#    shell '/bin/false'
#    system true
#  end
#
#  template '/etc/ceph/ceph.conf' do
#    mode '440'
#    owner 'ceph'
#    group 'ceph'
#    source "#{node.cloud.chef_version}/#{node.chef_environment}/ceph.conf.erb"
#  end
#
#  template '/etc/ceph/ceph.client.glance.keyring' do
#    mode '440'
#    owner 'ceph'
#    group 'ceph'
#    source "#{node.cloud.chef_version}/#{node.chef_environment}/ceph.client.glance.keyring.erb"
#  end
#end
