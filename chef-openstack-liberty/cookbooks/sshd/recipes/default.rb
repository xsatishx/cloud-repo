#
# Cookbook Name:: sshd
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

# We use the yates data bags for everything else, may as well put overrides in there
nodes = data_bag_item('yates', 'nodes')

overrides = { 'PermitRootLogin' => 'without-password', 'PasswordAuthentication' => 'no',
              'UsePAM' => 'no', 'AllowGroups' => 'staff', 'Ciphers' => 'aes256-ctr,blowfish-cbc',
              'MACs' => 'hmac-ripemd160,hmac-sha2-256,hmac-sha2-512', 'ListenAddress' => '0.0.0.0',
              'KexAlgorithms' => 'curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256' }
# #KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256
# #Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
# #MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-ripemd160-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512,hmac-sha2-256,hmac-ripemd160,umac-128@openssh.com

##

if nodes.include?(node.name) && nodes[node.name].include?('sshdoverride')
  overrides.merge!(nodes[node.name]['sshdoverride'])
elsif node.include?'sshdoverride'
  puts "**************************"
  puts overrides.to_json
  puts "----------------"
  puts node['sshdoverride'].to_json
  puts "**************************"
  overrides.merge!(node['sshdoverride'])
end

package 'openssh-server' do
  action :install
  action :upgrade
end

service 'ssh' do
  supports :restart => true, :status => true
  #action [:enable, :start]
end

template '/etc/ssh/sshd_config' do
  mode '644'
  owner 'root'
  group 'root'
  source 'sshd_config.erb'
  variables(:overrides => overrides)
  action :create
  notifies :restart, 'service[ssh]'
end

directory '/usr/local/etc/ssh/' do
  owner 'root'
  group 'root'
  mode '0700'
  action :create
end

cookbook_file '/usr/local/etc/ssh/krlfile' do
  source 'krlfile'
  mode '0600'
  owner 'root'
  group 'root'
  action :create
  notifies :restart, 'service[ssh]'
end
