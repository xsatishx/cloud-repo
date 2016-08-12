echo "Creating ceilometer user"
openstack user create --domain default --password healthseq ceilometer
openstack role add --project service --user ceilometer admin

echo "Creating neutron service"
openstack service create --name ceilometer --description "Telemetry" metering


echo "Creating Networking service API endpoints endpoints"

openstack endpoint create --region RegionOne metering public http://dev-controller:8777
openstack endpoint create --region RegionOne metering internal http://dev-controller:8777
openstack endpoint create --region RegionOne metering admin http://dev-controller:8777

