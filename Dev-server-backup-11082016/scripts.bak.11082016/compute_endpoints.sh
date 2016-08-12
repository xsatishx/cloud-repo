echo "Creating nova user"
openstack user create --domain default --password healthseq nova 
openstack role add --project service --user nova admin

echo "Creating nova service"
openstack service create --name nova --description "OpenStack Compute" compute

echo "Creating nova endpoints"
openstack endpoint create --region RegionOne compute public http://dev-controller:8774/v2/%\(tenant_id\)s
openstack endpoint create --region RegionOne compute internal http://dev-controller:8774/v2/%\(tenant_id\)s
openstack endpoint create --region RegionOne compute admin http://dev-controller:8774/v2/%\(tenant_id\)s
