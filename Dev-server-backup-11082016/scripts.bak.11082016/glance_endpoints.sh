echo "Creating Glance User"
openstack user create --domain default --password healthseq glance
openstack role add --project service --user glance admin

echo "Creating glance service"
openstack service create --name glance --description "OpenStack Image service" image

echo "Creating Glance endpoints"
openstack endpoint create --region RegionOne image public http://dev-controller:9292
openstack endpoint create --region RegionOne image internal http://dev-controller:9292
openstack endpoint create --region RegionOne image admin http://dev-controller:9292
