package "collectd-core" do
  action :install
  options '--no-install-recommends'
end

cookbook_file "/etc/collectd/collectd.conf" do
  source "collectd.conf"
  mode "0644"
  owner "root"
  group "root"
  notifies :restart, "service[collectd]"
end

service 'collectd' do
  action :start
end

directory "/etc/collectd/collectd.conf.d/" do
  action :create
  recursive true
  mode "0755"
  owner "root"
  group "root"
end

directory "/var/log/collectd/" do
  action :create
  recursive true
  mode "0755"
  owner "root"
  group "root"
end
