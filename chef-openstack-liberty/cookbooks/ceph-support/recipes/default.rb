#
# Cookbook Name:: ceph-support
#
# Copyright 2015, CDIS
#
# 🐙 support
#

template "/etc/sysctl.d/99-ceph.conf" do
  mode "440"
  owner "root"
  group "root"
  source "sysctl99-ceph.conf.erb"
  action :create
end

template "/etc/security/limits.d/99-ceph.conf" do
  mode "440"
  owner "root"
  group "root"
  source "limits.d99-ceph.conf.erb"
  action :create
end

directory "/opt" do
  mode "755"
  owner "root"
  group "root"
  action :create
end

#template "/opt/sas2ircu" do
#  mode "755"
#  owner "root"
#  group "root"
#  source "sas2ircu"
#  action :create
#end

cookbook_file "/opt/sas2ircu" do
  mode "755"
  owner "root"
  group "root"
  source "sas2ircu"
end

template "/etc/pam.d/common-session" do
  mode "644"
  owner "root"
  group "root"
  source "common-session.erb"
  action :create
end

template "/etc/pam.d/common-session-noninteractive" do
  mode "644"
  owner "root"
  group "root"
  source "common-session-noninteractive.erb"
  action :create
end
