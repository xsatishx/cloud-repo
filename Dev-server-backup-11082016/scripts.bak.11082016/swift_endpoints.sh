echo "Creating Swift user..."
openstack user create --domain default --password healthseq swift
openstack role add --project service --user swift admin

echo "Creating swift endpoints ... "
openstack service create --name swift --description "OpenStack Object Storage" object-store
openstack endpoint create --region RegionOne object-store public http://dev-controller:8080/v1/AUTH_%\(tenant_id\)s
openstack endpoint create --region RegionOne object-store internal http://dev-controller:8080/v1/AUTH_%\(tenant_id\)s
openstack endpoint create --region RegionOne object-store admin http://dev-controller:8080/v1
