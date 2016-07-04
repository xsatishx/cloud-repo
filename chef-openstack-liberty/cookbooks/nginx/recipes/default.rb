package "nginx" do
  action :install
  action :upgrade
end

service "nginx" do
  provider Chef::Provider::Service::Init
  supports :status => true, :restart => true, :stop => true, :start => true
  action [:restart]
end

template "/etc/nginx/sites-available/default" do
  mode "660"
  owner "root"
  group "root"
  source "#{node.chef_environment}/default.erb"
  notifies :restart, "service[nginx]"
end
