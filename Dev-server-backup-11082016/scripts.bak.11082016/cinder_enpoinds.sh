echo "Creating cinder User"
openstack user create --domain default --password healthseq cinder
openstack role add --project service --user cinder admin

echo "Creating cinder services"
openstack service create --name cinder --description "OpenStack Block Storage" volume
openstack service create --name cinderv2 --description "OpenStack Block Storage" volumev2

echo "Creating  Block Storage service API endpoints:"
openstack endpoint create --region RegionOne volume public http://dev-controller:8776/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne volume internal http://dev-controller:8776/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne volume admin http://dev-controller:8776/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne volumev2 public http://dev-controller:8776/v2/%\(tenant_id\)s
openstack endpoint create --region RegionOne volumev2 internal http://dev-controller:8776/v2/%\(tenant_id\)s
openstack endpoint create --region RegionOne volumev2 admin http://dev-controller:8776/v2/%\(tenant_id\)s

