#
# Cookbook Name:: nova-migration
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


user "nova" do
    shell "/bin/bash"
    action :modify
end

group "staff" do
    action :modify
    members "nova"
    append true
end

directory "/var/lib/nova/.ssh" do
    owner "nova"
    group "nova"
    mode "0700"
    action :create
end

template "/var/lib/nova/.ssh/id_rsa" do
    mode "0600"
    owner "nova"
    group "nova"
    source "id_rsa"
    action :create
end

template "/var/lib/nova/.ssh/config" do
    mode "0600"
    owner "nova"
    group "nova"
    source "config.erb"
    action :create
end

template "/var/lib/nova/.ssh/authorized_keys" do
    mode "0600"
    owner "nova"
    group "nova"
    source "authorized_keys"
    action :create
end
