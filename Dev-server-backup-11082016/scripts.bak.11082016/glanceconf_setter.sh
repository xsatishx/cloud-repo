crudini --set /etc/glance/glance-api.conf database connection mysql+pymysql://glance:healthseq@dev-controller/glance
crudini --del /etc/glance/glance-api.conf keystone_authtoken
crudini --set /etc/glance/glance-api.conf keystone_authtoken auth_uri http://dev-controller:5000
crudini --set /etc/glance/glance-api.conf keystone_authtoken auth_url http://dev-controller:35357
crudini --set /etc/glance/glance-api.conf keystone_authtoken auth_plugin password
crudini --set /etc/glance/glance-api.conf keystone_authtoken project_domain_id default
crudini --set /etc/glance/glance-api.conf keystone_authtoken user_domain_id default
crudini --set /etc/glance/glance-api.conf keystone_authtoken project_name service
crudini --set /etc/glance/glance-api.conf keystone_authtoken username glance
crudini --set /etc/glance/glance-api.conf keystone_authtoken password healthseq
crudini --set /etc/glance/glance-api.conf paste_deploy flavor keystone
crudini --set /etc/glance/glance-api.conf glance_store default_store file
crudini --set /etc/glance/glance-api.conf glance_store filesystem_store_datadir /var/lib/glance/images/
#crudini --set /etc/glance/glance-api.conf DEFAULT notification_driver noop
crudini --set /etc/glance/glance-api.conf DEFAULT verbose True
#Enable Image service meters
crudini --set /etc/glance/glance-api.conf notification_driver messagingv2
crudini --set /etc/glance/glance-api.conf DEFAULT rpc_backend rabbit
crudini --set /etc/glance/glance-api.conf oslo_messaging_rabbit rabbit_host dev-controller
crudini --set /etc/glance/glance-api.conf oslo_messaging_rabbit rabbit_userid openstack
crudini --set /etc/glance/glance-api.conf oslo_messaging_rabbit rabbit_password healthseq
#Edit the /etc/glance/glance-registry.conf file and complete the following actions
crudini --set /etc/glance/glance-registry.conf database connection mysql+pymysql://glance:healthseq@dev-controller/glance
crudini --del /etc/glance/glance-registry.conf keystone_authtoken
crudini --set /etc/glance/glance-registry.conf keystone_authtoken auth_uri http://dev-controller:5000
crudini --set /etc/glance/glance-registry.conf keystone_authtoken auth_url http://dev-controller:35357
crudini --set /etc/glance/glance-registry.conf keystone_authtoken auth_plugin password
crudini --set /etc/glance/glance-registry.conf keystone_authtoken project_domain_id default
crudini --set /etc/glance/glance-registry.conf keystone_authtoken user_domain_id default
crudini --set /etc/glance/glance-registry.conf keystone_authtoken project_name service
crudini --set /etc/glance/glance-registry.conf keystone_authtoken username glance
crudini --set /etc/glance/glance-registry.conf keystone_authtoken password healthseq
crudini --set /etc/glance/glance-registry.conf paste_deploy flavor keystone
#crudini --set /etc/glance/glance-registry.conf DEFAULT notification_driver noop
crudini --set /etc/glance/glance-registry.conf DEFAULT verbose True
#Enable Image service meters
crudini --set /etc/glance/glance-registry.conf notification_driver messagingv2
crudini --set /etc/glance/glance-registry.conf DEFAULT rpc_backend rabbit
crudini --set /etc/glance/glance-registry.conf oslo_messaging_rabbit rabbit_host dev-controller
crudini --set /etc/glance/glance-registry.conf oslo_messaging_rabbit rabbit_userid openstack
crudini --set /etc/glance/glance-registry.conf oslo_messaging_rabbit rabbit_password healthseq


