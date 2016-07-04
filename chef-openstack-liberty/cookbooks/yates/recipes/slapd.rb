#
# Cookbook Name:: yates
# Recipe:: slapd
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
end

package "slapd" do
  action :install
	#This preseeds debconf with our server password and common name
  #response_file "slapd.#{node.chef_environment}.opensciencedatacloud.org.seed"
  response_file "slapd/slapd.seed.#{node.chef_environment}.erb"
	#This is needed as I had dependency issues where it would restart slapd before creating the ssl
	## It also would run the scripts before creating the ldifs
  notifies :create, "cookbook_file[/etc/nsswitch.conf]", :immediately
  notifies :create, "directory[/etc/ldap/slapd.d/ssl]", :immediately
  notifies :create, "directory[/etc/ldap/slapd.d/ldifs]", :immediately
  notifies :create, "template[/etc/ldap/slapd.d/ldifs/enable_ldaps.ldif]", :immediately
  notifies :create, "template[/etc/ldap/slapd.d/ldifs/openstack_users.ldif]", :immediately
  notifies :create, "template[/root/slapd.source]", :immediately
  notifies :create, "cookbook_file[/etc/default/slapd]", :immediately
  notifies :create, "cookbook_file[/etc/ldap/slapd.d/ssl/ldap.#{node.chef_environment}.opensciencedatacloud.org.crt]", :immediately
  notifies :create, "cookbook_file[/etc/ldap/slapd.d/ssl/ldap.#{node.chef_environment}.opensciencedatacloud.org.key]", :immediately
  #Run the script to Enable SSL, it will restart slapd
  notifies :run, "script[enable_ldaps]", :immediately
  #Run the script to preload any user account.  
  notifies :run, "script[slapd_preusers]", :immediately
end

cookbook_file "/etc/nsswitch.conf" do
  source "slapd/nsswitch.conf"
  mode 0440
  owner "root"
  group "root"
end


service "slapd" do
  provider Chef::Provider::Service::Init::Debian
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

directory "/etc/ldap/slapd.d/ssl" do
  owner "openldap"
  group "openldap"
  mode 0550
end

directory "/etc/ldap/slapd.d/ldifs" do
  owner "openldap"
  group "openldap"
  mode 0550
end

#template "/etc/ldap/ldap.conf" do 
#  mode "440"
#  owner "root"
#  group "root"
#  source "slapd/ldap_ldap.conf.erb"
#  variables(
#	:chef_environment => "#{node.chef_environment}"
#  )
#end

#template "/etc/ldap.conf" do 
#  mode "440"
#  owner "root"
#  group "root"
#  source "slapd/ldap.conf.erb"
#  variables(
#	:chef_environment => "#{node.chef_environment}"
#  )
#end

template "/etc/ldap/slapd.d/ldifs/enable_ldaps.ldif" do 
  mode "440"
  owner "openldap"
  group "openldap"
  source "slapd/enable_ldaps.ldif.erb"
  variables(
	:chef_environment => "#{node.chef_environment}"
  )
end

template "/etc/ldap/slapd.d/ldifs/openstack_users.ldif" do 
  mode "440"
  owner "openldap"
  group "openldap"
  source "slapd/openstack_users.ldif.erb"
  variables(
	:chef_environment => "#{node.chef_environment}"
  )
end

template "/root/slapd.source" do 
  mode "440"
  owner "root"
  group "root"
  source "slapd/slapd.source.#{node.chef_environment}.erb"
  variables(
	:chef_environment => "#{node.chef_environment}"
  )
end

cookbook_file "/etc/ldap/slapd.d/ssl/ldap.#{node.chef_environment}.opensciencedatacloud.org.crt" do
  source "slapd/ldap.#{node.chef_environment}.opensciencedatacloud.org.crt"
  mode 0440
  owner "openldap"
  group "openldap"
end
cookbook_file "/etc/ldap/slapd.d/ssl/ldap.#{node.chef_environment}.opensciencedatacloud.org.key" do
  source "slapd/ldap.#{node.chef_environment}.opensciencedatacloud.org.key"
  mode 0440
  owner "openldap"
  group "openldap"
end
cookbook_file "/etc/default/slapd" do
  source "slapd/default_slapd"
  mode 0440
  owner "openldap"
  group "openldap"
end

script "enable_ldaps" do
  interpreter "bash"
  user "root"
  cwd "/tmp"
  not_if { node.attribute?("slapd_ssl_configed") }
  notifies :create, "ruby_block[slapd_ssl_configed]", :immediately
  notifies :restart, "service[slapd]", :immediately
  code <<-EOH
	source /root/slapd.source
	ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/slapd.d/ldifs/enable_ldaps.ldif
	service slapd restart
  EOH
end

script "slapd_preusers" do
  interpreter "bash"
  user "root"
  cwd "/tmp"
  not_if { node.attribute?("slapd_preusers") }
  notifies :create, "ruby_block[slapd_preusers_configed]", :immediately
  code <<-EOH
	source /root/slapd.source
	ldapmodify -a -x -D "cn=admin,${SLAPD_DC}" -w$SLAPD_PASS -f /etc/ldap/slapd.d/ldifs/openstack_users.ldif
  EOH
end

ruby_block "slapd_ssl_configed" do
  block do
    node.set['slapd_ssl_configed'] = true
    node.save
  end
  action :nothing
end
ruby_block "slapd_preusers_configed" do
  block do
    node.set['slapd_preusers'] = true
    node.save
  end
  action :nothing
end
