#
# Cookbook Name:: nova-client-pdc
# Recipe:: default
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#

packages = ['ceph-common',
            'nova-api-metadata',
            'nova-compute',
            'nova-compute-kvm',
            'nova-compute-libvirt',
            'nova-network',
            'open-iscsi',
            'python-guestfs',
            'xtightvncviewer']

services = ['nova-compute', 'nova-network', 'nova-api-metadata']

# Installing this first __should__ take care of the keys
package 'ubuntu-cloud-keyring' do
  action :install
  action :upgrade
end

apt_repository 'openstack' do
  uri 'http://ubuntu-cloud.archive.canonical.com/ubuntu'
  components ['main']
  distribution "#{node.lsb.codename}-updates/#{node.nova.version}"
  action :add
end

packages.each do |pkgname|
  package pkgname do
    action :install
    action :upgrade
  end
end

services.each do |srvname|
  service srvname do
    provider Chef::Provider::Service::Upstart
    supports status: true, restart: true, stop: true, start: true
  end
end

template '/etc/nova/nova.conf' do
  mode '700'
  owner 'nova'
  group 'nova'
  source "#{node.cloud.chef_version}/nova.conf.erb"
  notifies :restart, 'service[nova-compute]'
  notifies :restart, 'service[nova-network]'
  notifies :restart, 'service[nova-api-metadata]'
end

template '/etc/nova/secret.xml' do
  mode '400'
  owner 'root'
  group 'root'
  source "#{node.cloud.chef_version}/secret.xml.erb"
end

template '/root/set_virsh_ceph_secret.sh' do
  mode '400'
  owner 'root'
  group 'root'
  source "#{node.cloud.chef_version}/set_virsh_ceph_secret.sh.erb"
end

cookbook_file '/etc/kernel/postinst.d/statoverride' do
  source "#{node.cloud.chef_version}/stateoverride"
  mode 0770
  owner 'root'
  group 'root'
  action :create
end

cookbook_file '/etc/nova/patch_bug_1219658.patch' do
  source "#{node.cloud.chef_version}/patch_bug_1219658.patch"
  mode 0770
  owner 'root'
  group 'root'
  action :create
end

execute 'statoverride' do
  command 'dpkg-statoverride  --update --add root root 0644 /boot/vmlinuz-$(uname -r) || /bin/true'
  action :run
end
