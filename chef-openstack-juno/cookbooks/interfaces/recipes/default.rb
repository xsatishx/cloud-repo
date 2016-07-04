#
# Cookbook Name:: interfaces
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

bonding_packages=["ifenslave","ethtool"]

nodes = data_bag_item("yates", "nodes")

data=nodes[node.name]


#install this everywhere
package("bridge-utils"){action :install}

template "/etc/network/interfaces" do
  owner "root"
  group "root"
  action :create
  source "etcnetworkinterfaces.erb"
end

#we don't need ipv6, lets just disable it
template "/etc/sysctl.d/90-disableipv6.conf" do
  owner "root"
  group "root"
  action :create
  source "sysctl.erb"
end

remote_directory '/etc/network/interfaces.d/' do
  owner "root"
  group "root"
  mode 0775
  files_owner "root"
  files_group "root"
  files_mode 0554
  recursive true
  action :create 
end

if data.include?"bonds" and not(data["bonds"].empty?)
  puts ""
  puts ""
  puts "Founding bonding config"
  puts ""
  puts ""
  bonding_packages.each do
  |bpkg|
    package bpkg do
      action :install
    end
  end

  bonds=data["bonds"]

  usedinbond=[]

  data["bonds"].each do
  |bond|
    data[bond]["interface"]=bond #ugly, but it keeps the templates simpler
    #Actual bonded interfaces
    template "/etc/network/interfaces.d/#{bond.gsub(".","_")}" do
      mode "664"
      owner "root"
      group "root"
      source "bond.erb"
      variables(data[bond])
    end
    #slaves
    data[bond]["slaves"].each do
    |slave|
      template "/etc/network/interfaces.d/#{slave}" do
        mode "664"
        owner "root"
        group "root"
        source "slave.erb"
        variables({:master=>bond,:slave=>slave})
      end
      usedinbond << slave
    end
  end

  #Bridges
  puts ""
  puts ""
  puts ""
  puts "About to try and configure bridges"
  puts ""
  puts ""
  puts ""
  if data.include?"bridges" and not(data["bridges"].empty?)
    data["bridges"].each do
    |bridge|
      data[bridge]["interface"]=bridge #Still necessary to populate the file
      template "/etc/network/interfaces.d/#{bridge.gsub(".","_")}" do
        mode "664"
        owner "root"
        group "root"
        source "bridge.erb"
        #puts data[bridge].to_json
        variables(data[bridge])
      end
    end
  else
    puts ""
    puts ""
    puts ""
    puts "No bridges found"
    puts ""
    puts ""
    puts ""
  end


  #Other configured interfaces
  if data.include?"interfaces"
  puts ""
  puts ""
  puts "processing other nics in bonding config"
  puts ""
  puts ""
    data["interfaces"].each do
    |interface| 
      next if usedinbond.include?interface
      if(data.include?"bridges")
        next if data["bridges"].include?interface
      end
      template "/etc/network/interfaces.d/#{interface.gsub(".","_")}" do
        mode "664"
        owner "root"
        group "root"
        source "interface.erb"
        #this is disgusting, Kyle, fix this
        data[interface][:interface]=interface
        variables(data[interface])
      end
    end
  end
else
  puts ""
  puts ""
  puts "Didn't find bonding config"
  puts ""
  puts ""
  #Bridges
  puts ""
  puts ""
  puts ""
  puts "About to try and configure bridges"
  puts ""
  puts ""
  puts ""
  if data.include?"bridges" and not(data["bridges"].empty?)
    data["bridges"].each do
    |bridge|
      data[bridge]["interface"]=bridge
      template "/etc/network/interfaces.d/#{bridge.gsub(".","_")}" do
        mode "664"
        owner "root"
        group "root"
        source "bridge.erb"
        variables(data[bridge])
      end
    end
  else
    puts ""
    puts ""
    puts ""
    puts "No bridges found"
    puts ""
    puts ""
    puts ""
  end

  if data.include?"interfaces"
    #configured interfaces, no bonding
    data["interfaces"].each do
    |interface| 
      if(data.include?"bridges" and data["bridges"].include?interface)
        next
      end
      template "/etc/network/interfaces.d/#{interface.gsub(".","_")}" do
        mode "664"
        owner "root"
        group "root"
        source "interface.erb"
        #this is disgusting, Kyle, fix this
        data[interface][:interface]=interface
        variables(data[interface])
      end
    end
  else
    puts ""
    puts ""
    puts "no interfaces array?!?"
    puts ""
    puts ""
  end
end
