#
# Cookbook Name:: syslog-ng
# Recipe:: default
#
# Copyright 2014, Laboratory for Advanced Computing
#
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


package "syslog-ng" do
  action :install
end

service "syslog-ng" do
  provider Chef::Provider::Service::Init::Debian
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:enable, :start]
end

template "/etc/syslog-ng/conf.d/01-remote.conf" do 
  mode "640"
  owner "root"
  group "root"
  source "01-remote.conf.#{node.chef_environment}.erb"
  variables(
  )
  notifies :restart, "service[syslog-ng]"
end

#template "/etc/ssl/private/syslog.opensciencedatacloud.org.key" do 
#  mode "700"
#  owner "root"
#  group "root"
#  source "syslog.opensciencedatacloud.org.crt.erb"
#  variables(
#  )
#  notifies :restart, "service[syslog-ng]"
#end
#
#template "/etc/ssl/certs/syslog.opensciencedatacloud.org.crt" do 
#  mode "700"
#  owner "root"
#  group "root"
#  source "syslog.opensciencedatacloud.org.key.erb"
#  variables(
#  )
#  notifies :restart, "service[syslog-ng]"
#end
