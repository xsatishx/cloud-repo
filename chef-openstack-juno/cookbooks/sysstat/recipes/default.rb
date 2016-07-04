#
# Cookbook Name:: sysstat
# Recipe:: default
package "sysstat" do
  action :install
end

service "sysstat" do
  supports :restart => true, :status => true
  action [:enable, :start]
end

template "/etc/default/sysstat" do
  owner "root"
  group "root"
  action :create
  source "sysstat.erb"
end
