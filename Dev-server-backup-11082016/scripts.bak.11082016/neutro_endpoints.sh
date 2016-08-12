echo "Creating neutron User"
openstack user create --domain default --password healthseq neutron
openstack role add --project service --user neutron admin

echo "Creating neutron service"
openstack service create --name neutron --description "OpenStack Networking" network

echo "Creating Networking service API endpoints endpoints"
openstack endpoint create --region RegionOne network public http://dev-controller:9696
openstack endpoint create --region RegionOne network internal http://dev-controller:9696
openstack endpoint create --region RegionOne network admin http://dev-controller:9696


