package "memcached" do
  action :install
  action :upgrade
end

service "memcached" do
  provider Chef::Provider::Service::Init
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:restart]
end

template "/etc/memcached.conf" do
  mode "660"
  owner "memcache"
  group "memcache"
  source "#{node.chef_environment}/memcached.conf.erb"
  notifies :restart, "service[memcached]"
end
