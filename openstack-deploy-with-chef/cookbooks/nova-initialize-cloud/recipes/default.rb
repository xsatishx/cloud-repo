#
# Cookbook Name:: nova-initialize-pdc
# Recipe:: default
#
# Copyright 2013, HealthSeq
#
# All rights reserved - Do Not Redistribute
#

template "/root/creds_source" do
  mode "440"
  owner "openldap"
  group "openldap"
  source "creds_source.#{node.chef_environment}.erb"
  variables(
  )
  action :create
end

#The version provided with keystone is to primitive, cant pull dynamically as they introduce
## changes to variable names that can break stuff.  
cookbook_file "/root/sample_data.sh" do
  source "sample_data.sh"
  mode 0550
  owner "root"
  group "root"
  action :create
end

cookbook_file "/root/init_mysql.sh" do
  source "init_mysql.sh"
  mode 0550
  owner "root"
  group "root"
  action :create
end

script "openstack_initialize" do
  interpreter "bash"
  user "root"
  cwd "/tmp"
  not_if { node.attribute?("openstack_initialized") }
  notifies :create, "ruby_block[openstack_initialize]", :immediately
  code <<-EOH
	source /root/creds_source
	/root/init_mysql.sh

	#init the mysql keystone db
	service keystone restart
	keystone-manage db_sync
	/root/sample_data.sh > /root/sample_data.out &2>1

	#init glance
	glance-manage version_control 0
	glance-manage db_sync
	service glance-registry restart
	service glance-api restart

	#init nova
	nova-manage db sync
    	for svc in api network volume scheduler cert; do sudo service nova-$svc stop ; done
    	for svc in api network volume scheduler cert; do sudo service nova-$svc start ; done
     
	#Network:
	nova-manage network create private --fixed_range_v4=172.16.0.0/16 --bridge=virbr1 --bridge_interface=eth2 --num_networks=1 --network_size=65536
    	mysql -unova -p$MYSQL_nova_PASS nova -e'update fixed_ips set reserved="1" where id < 257 ;'
    	mysql -unova -p$MYSQL_nova_PASS nova -e'update networks set dhcp_start="172.16.1.0" where cidr="172.16.0.0/16"';
 

  EOH
end

ruby_block "openstack_initialize" do
  block do
    node.set['openstack_initialized'] = true
    node.save
  end
  action :nothing
end
