#
# Cookbook Name:: lac-iptables
# Recipe:: default
#
# Copyright 2013, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#

package "samba" do
  action :install
end

service "smbd" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action :nothing
end
service "nmbd" do
  provider Chef::Provider::Service::Upstart
  supports :status => true, :restart => true, :stop => true, :start => true
  action :nothing
end


template "/etc/samba/smb.conf" do
  source "smb.conf.#{node.chef_environment}.erb"
  mode "755"
  owner "root"
  group "root"
  notifies :restart, "service[smbd]"
  variables(
        :chef_environment => "#{node.chef_environment}"
  )
end

# Commented out, it stopped working in trusty.  Not sure why.
# run smbpasswd -w$PASS to do manually for now
#cookbook_file "/var/lib/samba/secrets.tdb" do
#  source "secrets.#{node.chef_environment}.tdb"
#  mode 0500
#  owner "root"
#  group "root"
#end
