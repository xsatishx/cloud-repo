#
# Cookbook Name:: luks
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

package "cryptsetup-luks" do
  action :install
end
package "xfsprogs" do
  action :install
end
package "haveged" do
  action :install
end

service "haveged" do
  provider Chef::Provider::Service::Init
  supports :status => true, :restart => true, :stop => true, :start => true
end



directory "/etc/luks" do
  owner "root"
  group "root"
  mode 0700
  action :create
end

cookbook_file "/etc/luks/keyfile" do
  source "#{node.chef_environment}/keyfile"
  mode 0440
  owner "root"
  group "root"
end

cookbook_file "/etc/crypttab" do
  source "#{node.chef_environment}/crypttab"
  mode 0440
  owner "root"
  group "root"
end

## Once installed you need to run
#Format
# yes | cryptsetup --cipher aes-xts-plain64 --hash sha512 --iter-time 5000 --use-random --verify-passphrase luksFormat  --key-file /etc/luks/keyfile  /dev/sdb1
# yes | cryptsetup --cipher aes-xts-plain64 --hash sha512 --iter-time 5000 --use-random --verify-passphrase luksFormat  --key-file /etc/luks/keyfile  /dev/sdc1
# echo "/dev/mapper/bricks_sdb1    /exports/gluster/bricks_sdb1    xfs    defaults    0 0" >> /etc/fstab
# echo "/dev/mapper/bricks_sdc1    /exports/gluster/bricks_sdc1    xfs    defaults    0 0" >> /etc/fstab

