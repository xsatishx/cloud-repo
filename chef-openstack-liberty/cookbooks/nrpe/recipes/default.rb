#
# Cookbook Name:: nrpe
# Recipe:: default

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


package "nagios-nrpe-server" do
  action :install
end
package "clamav" do
  action :install
end
#Must run freshclam to actually have the definitions file it need to run clamav
#execute 'freshclam'
service "nagios-nrpe-server" do
  provider Chef::Provider::Service::Init
  supports :status => true, :restart => true, :stop => true, :start => true
  #action [ :start, :restart]
end

if(node.include?"cloud")
 if(node.cloud.chef_version=="atwood")
  package "debsums" do
   action :install
  end
#  package "acct" do
#    action :install
#  end
#  directory '/usr/local/var/log/auditscript' do
#    owner 'root'
#    group 'root'
#    mode '0644'
#    action :create
#  end
 end
end

template "/etc/nagios/nrpe.d/nrpe_checks.cfg" do
  mode "544"
  owner "root"
  group "root"
  #puts JSON.pretty_generate(node)
  # I thought there was some way to automate this sort of logic in chef?
  if(node.include?"cloud")
    source "#{node.cloud.chef_version}/nrpe_checks.cfg.erb"
  else
    source "nrpe_checks.cfg.erb"
  end
  action :create
  notifies :restart, "service[nagios-nrpe-server]"
end
template "/etc/nagios/nrpe.d/allowed_hosts.cfg" do
  mode "544"
  owner "root"
  group "root"
  source "allowed_hosts.cfg.erb"
  action :create
  notifies :restart, "service[nagios-nrpe-server]"
end
template "/etc/nagios/nrpe.cfg" do
  mode "544"
  owner "root"
  group "root"
  source "nrpe.cfg.erb"
  action :create
  notifies :restart, "service[nagios-nrpe-server]"
end
template "/etc/sudoers.d/nagios_sudoers" do
  mode "440"
  owner "root"
  group "root"
  source "nagios_sudoers.erb"
  action :create
  notifies :restart, "service[nagios-nrpe-server]"
end

remote_directory '/usr/lib/nagios/osdc-plugins/' do
  source "osdc-plugins"
  owner "nagios"
  group "nagios"
  mode 0770
  files_owner "nagios"
  files_group "nagios"
  files_mode 00544
  recursive true
  action :create 
  notifies :restart, "service[nagios-nrpe-server]"
end

#Another template, but this needs that directory to exist
#Kyle this is gross, fix.
template "/usr/lib/nagios/osdc-plugins/canary.sh" do
  mode "754"
  owner "root"
  group "root"
  source "canary.sh.erb"
  action :create
end

#For files the osdc-plugins might need
remote_directory '/usr/local/share/osdc-plugins/' do
  source "shareosdcplugins"
  owner "nagios"
  group "nagios"
  mode 0755
  files_owner "nagios"
  files_group "nagios"
  files_mode  0644
  recursive true
  action :create
  notifies :restart, "service[nagios-nrpe-server]"
end

#For supplimental scripts the osdc plugins may rely upon
remote_directory '/usr/local/bin/' do
  source "usrlocalbin"
  owner "root"
  group "root"
  mode 0755
  files_owner "root"
  files_group "root"
  files_mode 00755
  recursive true
  action :create_if_missing
  notifies :restart, "service[nagios-nrpe-server]"
end

link '/etc/cron.daily/runclamscan' do
    link_type :symbolic
    owner 'root'
    group 'root'
    to '/usr/local/bin/runclamscan.sh'
end
