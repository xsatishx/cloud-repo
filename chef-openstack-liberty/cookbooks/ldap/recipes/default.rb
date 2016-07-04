#
# Cookbook Name:: slapd-pdc
# Recipe:: default
#
# Copyright 2013, Laboratory for Advanced Computing
#
# All rights reserved - Do Not Redistribute
#
#

package "libldap-2.4-2" do
  action :install
end

package "ldap-utils" do
  action :install
  notifies :create, "template[/etc/ldap/ldap.conf]", :immediately
  notifies :create, "template[/etc/ldap.conf]", :immediately
  notifies :create, "cookbook_file[/etc/nsswitch.conf]", :immediately
end

package "libnss-ldap" do
  action :install
end

template "/etc/ldap/ldap.conf" do 
  mode "440"
  owner "root"
  group "root"
  source "#{node.chef_environment}/ldap_ldap.conf.erb"
  variables(
	:chef_environment => "#{node.chef_environment}"
  )
end

template "/etc/ldap.conf" do 
  mode "440"
  owner "root"
  group "root"
  source "#{node.chef_environment}/ldap.conf.erb"
  variables(
	:chef_environment => "#{node.chef_environment}"
  )
end

cookbook_file "/etc/nsswitch.conf" do
  source "nsswitch.conf"
  mode 0440
  owner "root"
  group "root"
end
