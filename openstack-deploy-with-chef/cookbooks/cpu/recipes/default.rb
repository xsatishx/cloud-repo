#
# Cookbook Name:: cpu
# Recipe:: pdcv3
#

#

package "cpu" do
  action :install
  action :upgrade
end
template "/etc/cpu/cpu.conf" do 
  mode "440"
  owner "root"
  group "root"
  source "#{node.cloud.chef_version}/cpu.conf.erb"
end


