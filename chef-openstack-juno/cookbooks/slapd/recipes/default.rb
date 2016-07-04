#
# Cookbook Name:: slapd-pdc
# Recipe:: default
#
# Copyright 2013, HealthSeq
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
  # need to create the files/ENVIRONMENT_NAME/slapd.seed.erb for each environment
  #response_file "#{node.chef_environment}/slapd.seed.erb"
  response_file "#{node.cloud.chef_version}/slapd.seed.erb"
	#This is needed as I had dependency issues where it would restart slapd before creating the ssl
	## It also would run the scripts before creating the ldifs
  notifies :create, "directory[/etc/ldap/slapd.d/ssl]", :immediately
  notifies :create, "directory[/etc/ldap/slapd.d/ldifs]", :immediately
  notifies :create, "template[/etc/ldap/slapd.d/ldifs/enable_ldaps.ldif]", :immediately
  notifies :create, "template[/root/slapd.source]", :immediately
  notifies :create, "cookbook_file[/etc/default/slapd]", :immediately
  notifies :create, "template[/etc/ldap/slapd.d/ssl/ldap.opensciencedatacloud.org.crt]", :immediately
  notifies :create, "template[/etc/ldap/slapd.d/ssl/ldap.opensciencedatacloud.org.key]", :immediately
  notifies :create, "template[/etc/ldap/slapd.d/ssl/ca-bundle.crt]", :immediately
  #Run the script to Enable SSL, it will restart slapd
  notifies :run, "script[enable_ldaps]", :immediately
  #Run the script to preload any user account.  , not needed anymore
  #notifies :create, "template[/etc/ldap/slapd.d/ldifs/openstack_users.ldif]", :immediately
  #notifies :run, "script[slapd_preusers]", :immediately
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

template "/etc/ldap/slapd.d/ldifs/enable_ldaps.ldif" do 
  mode "440"
  owner "openldap"
  group "openldap"
  source "#{node.cloud.chef_version}/enable_ldaps.ldif.erb"
end

template "/etc/ldap/slapd.d/ldifs/openstack_users.ldif" do 
  mode "440"
  owner "openldap"
  group "openldap"
  source "#{node.cloud.chef_version}/openstack_users.ldif.erb"
end

template "/root/slapd.source" do 
  mode "440"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/slapd.source.erb"
end

template "/etc/pam_ldap.secret" do 
  mode "400"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/pam_ldap.secret.erb"
end

#cookbook_file "/etc/ldap/slapd.d/ssl/ldap.opensciencedatacloud.org.crt" do
#  source "#{node.cloud.chef_version}/ldap.opensciencedatacloud.org.crt"
#  mode 0440
#  owner "openldap"
#  group "openldap"
#end
#cookbook_file "/etc/ldap/slapd.d/ssl/ldap.opensciencedatacloud.org.key" do
#  source "#{node.cloud.chef_version}/ldap.opensciencedatacloud.org.key"
#  mode 0440
#  owner "openldap"
#  group "openldap"
#end
cookbook_file "/etc/default/slapd" do
  source "#{node.cloud.chef_version}/default_slapd"
  mode 0440
  owner "openldap"
  group "openldap"
end

template "/etc/security/limits.d/openldap.conf" do
  mode "444"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/limits.d/openldap.conf.erb"
end
template  "/etc/ldap/slapd.d/ssl/ldap.opensciencedatacloud.org.crt" do
  mode 0440
  owner "openldap"
  group "openldap"
  source "#{node.cloud.chef_version}/ssl.crt.erb"
end
template "/etc/ldap/slapd.d/ssl/ldap.opensciencedatacloud.org.key" do
  mode 0440
  owner "openldap"
  group "openldap"
  source "#{node.cloud.chef_version}/ssl.key.erb"
end
template "/etc/ldap/slapd.d/ssl/ca-bundle.crt" do
  mode 0440
  owner "openldap"
  group "openldap"
  source "#{node.cloud.chef_version}/ca-bundle.crt.erb"
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


