#
# Cookbook Name:: nicities
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

#I don't really like this, but apparently there is no current chef-ordained way of
#checking for installed packages
#Also, this needs to be global $, not class instance level @
$packages=Hash.new(){|h,k|h[k]=[]}
%x{dpkg --get-selections|grep syslog}.scan(/^([\S]+)[\s]+([\S]+)/).each{|a,b| $packages[b] << a}
#For those that don't read ugly ruby oneliner
#Hash.new(){|h,k|h[k]=[]} creates a new hash, where requesting a missing key automatically
# creates a blank array and assigns it for that key
#%x{} runs the command on shell, and returns the stdout
#.scan() applies a regex to the text, line by line, and returns an array of matches
#/^([\S]+)[\s]+([\S]+)/ matches text, a space, and more text, and keeps only the two texts
#.each here is taking the array of matches, and using those to puplate the $packages hash

nicities={"/etc/default/irqbalance"=>"irqbalance",
"/etc/vim/vimrc.local"=>"vimrc.local",
"/etc/skel/.irbrc"=>"irbrc",
"/etc/default/sysstat"=>"sysstat.erb",
"/etc/rsyslog.d/60-remote.conf"=>"remotesyslog.erb",
"/etc/profile.d/seteditor.sh"=>"seteditor.sh",
"/etc/profile.d/sethistory.sh"=>"sethistory.sh.erb",
"/etc/default/smartmontools"=>"smartmontools.erb",
"/etc/smartd.conf"=>"smartd.conf.erb",
"/etc/rsyslog.d/50-default.conf"=>"rsyslogdefaults.erb",
"/etc/sudoers.d/staff_sudoers"=>"staff_sudoers.erb"}

#We need a way of triggering service restarts.  OK, maybe hits recipe needs nicing up
service={"/etc/rsyslog.d/60-remote.conf"=>"rsyslog","/etc/smartd.conf"=>"smartmontools"}

#These don't need their own recipies
package("sysstat"){action :install}
service "sysstat" do
  supports :restart => true, :status => true
  action [:enable, :start]
end

if($packages['install'].include?'rsyslog')
  #rsyslog should be on MOST of the old systems, but some have syslog-ng
  service "rsyslog" do
    provider(Chef::Provider::Service::Upstart)
    supports :restart => true, :stop=> true, :start=> true, :status => true
    action [:enable]
    action [:restart]
  end
elsif($packages['install'].include?'syslog-ng')
  puts "#### We would do something here, if this recipie supported syslog-ng"
else
  puts "####"
  puts "####"
  puts "####"
  puts "####"
  puts "#### Is no syslog daemon of any sort installed?  Look at this node!"
  puts "####"
  puts "####"
  puts "####"
end

package("smartmontools"){action :install}
service "smartmontools" do
  supports :restart => true, :status => true
  action [:enable,:start]
end

nicities.each do
|target,source|
  template target do
    if target =~ /rc/
      mode "644"
    else
      mode "640"
    end
    owner "root"
    group "root"
    source source
    action :create
    if(service.include?target)
      servicename=service[target]
      puts "Working on #{servicename}"
      if(servicename=='rsyslog')
        next unless $packages['install'].include?'rsyslog'
        notifies :restart, "service[#{service[target]}]" if service.include?target
      else
        notifies :restart, "service[#{service[target]}]" if service.include?target
      end
    end
  end
end


