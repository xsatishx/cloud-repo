crudini --set /etc/cinder/cinder.conf database connection  mysql+pymysql://cinder:healthseq@dev-controller/cinder
crudini --set /etc/cinder/cinder.conf DEFAULT rpc_backend rabbit
crudini --set /etc/cinder/cinder.conf oslo_messaging_rabbit rabbit_host dev-controller
crudini --set /etc/cinder/cinder.conf oslo_messaging_rabbit rabbit_userid openstack
crudini --set /etc/cinder/cinder.conf oslo_messaging_rabbit rabbit_password healthseq
crudini --set /etc/cinder/cinder.conf DEFAULT auth_strategy keystone
crudini --del /etc/cinder/cinder.conf keystone_authtoken
crudini --set /etc/cinder/cinder.conf keystone_authtoken auth_uri http://dev-controller:5000
crudini --set /etc/cinder/cinder.conf keystone_authtoken auth_url http://dev-controller:35357
crudini --set /etc/cinder/cinder.conf keystone_authtoken auth_plugin password
crudini --set /etc/cinder/cinder.conf keystone_authtoken project_domain_id default
crudini --set /etc/cinder/cinder.conf keystone_authtoken user_domain_id default
crudini --set /etc/cinder/cinder.conf keystone_authtoken project_name service
crudini --set /etc/cinder/cinder.conf keystone_authtoken username cinder
crudini --set /etc/cinder/cinder.conf keystone_authtoken password healthseq
crudini --set /etc/cinder/cinder.conf DEFAULT my_ip 10.0.2.13
crudini --set /etc/cinder/cinder.conf oslo_concurrency lock_path /var/lib/cinder/tmp
crudini --set /etc/cinder/cinder.conf DEFAULT verbose True
