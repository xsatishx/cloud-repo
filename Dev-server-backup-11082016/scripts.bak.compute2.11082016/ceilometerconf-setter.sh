crudini --set /etc/ceilometer/ceilometer.conf database connection mongodb://ceilometer:healthseq@dev-controller:27017/ceilometer
crudini --set /etc/ceilometer/ceilometer.conf DEFAULT rpc_backend rabbit
crudini --set /etc/ceilometer/ceilometer.conf oslo_messaging_rabbit rabbit_host dev-controller
crudini --set /etc/ceilometer/ceilometer.conf oslo_messaging_rabbit rabbit_userid openstack
crudini --set /etc/ceilometer/ceilometer.conf oslo_messaging_rabbit rabbit_password healthseq
crudini --set /etc/ceilometer/ceilometer.conf DEFAULT auth_strategy keystone
crudini --del /etc/ceilometer/ceilometer.conf keystone_authtoken
crudini --set /etc/ceilometer/ceilometer.conf keystone_authtoken auth_uri http://dev-controller:5000
crudini --set /etc/ceilometer/ceilometer.conf keystone_authtoken auth_url http://dev-controller:35357
crudini --set /etc/ceilometer/ceilometer.conf keystone_authtoken auth_plugin password
crudini --set /etc/ceilometer/ceilometer.conf keystone_authtoken project_domain_id default
crudini --set /etc/ceilometer/ceilometer.conf keystone_authtoken user_domain_id default
crudini --set /etc/ceilometer/ceilometer.conf keystone_authtoken project_name service
crudini --set /etc/ceilometer/ceilometer.conf keystone_authtoken username ceilometer
crudini --set /etc/ceilometer/ceilometer.conf keystone_authtoken password healthseq
crudini --set /etc/ceilometer/ceilometer.conf service_credentials os_auth_url http://dev-controller:5000/v2.0
crudini --set /etc/ceilometer/ceilometer.conf service_credentials os_username ceilometer
crudini --set /etc/ceilometer/ceilometer.conf service_credentials os_tenant_name service
crudini --set /etc/ceilometer/ceilometer.conf service_credentials os_password healthseq
crudini --set /etc/ceilometer/ceilometer.conf service_credentials os_endpoint_type internalURL
crudini --set /etc/ceilometer/ceilometer.conf service_credentials os_region_name RegionOne
crudini --set /etc/ceilometer/ceilometer.conf DEFAULT verbose True

