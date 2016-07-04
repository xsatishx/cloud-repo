#
# Cookbook Name:: slapd-pdc
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#
#

package "xinetd" do
  action :install
end

package "quotatool" do
  action :install
end

package "quota" do
  action :install
  notifies :create, "cookbook_file[/etc/xinetd.d/repquota]", :immediately
  notifies :create, "cookbook_file[/usr/local/sbin/repquota_gluster.sh]", :immediately
  notifies :create, "cookbook_file[/usr/local/sbin/enable_quota_on_brick.sh]", :immediately
end

cookbook_file "/etc/xinetd.d/repquota" do
  source "repquota.xinetd"
  mode 0440
  owner "root"
  group "root"
end
cookbook_file "/usr/local/sbin/repquota_gluster.sh" do
  if node.chef_environment == "l05" then
	source "repquota_gluster.#{node.chef_environment}.sh"
  else
	source "repquota_gluster.sh"
  end
  mode 0550
  owner "root"
  group "root"
end
cookbook_file "/usr/local/sbin/enable_quota_on_brick.sh" do
  source "enable_quota_on_brick.sh"
  mode 0550
  owner "root"
  group "root"
end
