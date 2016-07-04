#
# Cookbook Name:: yates
# Recipe:: dhcpd
#
# Copyright 2013, rafael
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

package "isc-dhcp-server" do
	action :install
end

service "isc-dhcp-server" do
	provider Chef::Provider::Service::Upstart
	supports :restart => true, :reload => true, :status => true
end

#pxe_hosts = data_bag_item("yates", "pxe_hosts_old")
#hosts = pxe_hosts['hosts']
#clouds = pxe_hosts['clouds']

#nodes = data_bag_item("yates", "pxe_hosts")
nodes = data_bag_item("yates", "nodes")
reservations = data_bag_item("yates","reservations")
racks = data_bag_item("yates", "racks")
forms = data_bag_item("yates", "forms")
builds = forms['builds']

template "/etc/dhcp/dhcpd.conf" do
  mode "644"
  owner "root"
  group "root"
  source "dhcp/dhcpd.conf.erb"
  variables({
#    :hosts => hosts,
#    :clouds => clouds,
    :nodes => nodes,
    :racks => racks,
    :forms => forms,
    :builds => builds,
    :reservations => reservations
    })
  action :create
  notifies :restart, "service[isc-dhcp-server]"
end
