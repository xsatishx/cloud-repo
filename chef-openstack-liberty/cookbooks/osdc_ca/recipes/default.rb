#
# Cookbook Name:: osdc_ca
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#

package "ca-certificates" do
  action :install
  action :upgrade
end

cookbook_file "/usr/local/share/ca-certificates/osdc_ca.crt" do
  source "osdc_ca.crt"
  mode 0664
  owner "root"
  group "root"
  action :create
  notifies :run, "execute[update-ca-certificates]"
end

cookbook_file "/usr/local/share/ca-certificates/comodo_bundle.crt" do
  source "osdc_ca.crt"
  mode 0664
  owner "root"
  group "root"
  action :create
  notifies :run, "execute[update-ca-certificates]"
end

execute "update-ca-certificates" do
  command "update-ca-certificates"
  action :run
end

