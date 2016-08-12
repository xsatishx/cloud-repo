crudini --set /etc/heat/heat.conf database connection mysql+pymysql://heat:healthseq@dev-controller/heat
crudini --set /etc/heat/heat.conf DEFAULT rpc_backend rabbit
crudini --set /etc/heat/heat.conf oslo_messaging_rabbit rabbit_host dev-controller
crudini --set /etc/heat/heat.conf oslo_messaging_rabbit rabbit_userid openstack
crudini --set /etc/heat/heat.conf oslo_messaging_rabbit rabbit_password healthseq
crudini --set /etc/heat/heat.conf DEFAULT auth_strategy keystone
crudini --del /etc/heat/heat.conf keystone_authtoken
crudini --set /etc/heat/heat.conf keystone_authtoken auth_uri http://dev-controller:5000
crudini --set /etc/heat/heat.conf keystone_authtoken auth_url http://dev-controller:35357
crudini --set /etc/heat/heat.conf keystone_authtoken auth_plugin password
crudini --set /etc/heat/heat.conf keystone_authtoken project_domain_id default
crudini --set /etc/heat/heat.conf keystone_authtoken user_domain_id default
crudini --set /etc/heat/heat.conf keystone_authtoken project_name service
crudini --set /etc/heat/heat.conf keystone_authtoken username heat
crudini --set /etc/heat/heat.conf keystone_authtoken password healthseq

crudini --set /etc/heat/heat.conf trustee auth_plugin password
crudini --set /etc/heat/heat.conf trustee auth_url http://dev-controller:35357
crudini --set /etc/heat/heat.conf trustee username heat
crudini --set /etc/heat/heat.conf trustee password healthseq
crudini --set /etc/heat/heat.conf trustee user_domain_id default

crudini --set /etc/heat/heat.conf clients_keystone auth_uri http://dev-controller:5000
crudini --set /etc/heat/heat.conf ec2authtoken auth_uri http://dev-controller:5000/v3

crudini --set /etc/heat/heat.conf DEFAULT heat_metadata_server_url http://dev-controller:8000
crudini --set /etc/heat/heat.conf DEFAULT heat_waitcondition_server_url http://dev-controller:8000/v1/waitcondition
crudini --set /etc/heat/heat.conf DEFAULT stack_domain_admin heat_domain_admin
crudini --set /etc/heat/heat.conf DEFAULT stack_domain_admin_password healthseq
crudini --set /etc/heat/heat.conf DEFAULT stack_user_domain_name heat
crudini --set /etc/heat/heat.conf DEFAULT verbose true
