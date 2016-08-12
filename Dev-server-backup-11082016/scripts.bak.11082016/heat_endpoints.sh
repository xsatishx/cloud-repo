echo "Creating heat user..."
#openstack user create --domain default --password healthseq heat
openstack role add --project service --user heat admin

echo "Creating services..."
openstack service create --name heat  --description "Orchestration" orchestration
openstack service create --name heat-cfn --description "Orchestration"  cloudformation

echo "Creating endpoints... "
openstack endpoint create --region RegionOne orchestration public http://dev-controller:8004/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne orchestration internal http://dev-controller:8004/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne orchestration admin http://dev-controller:8004/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne cloudformation public http://dev-controller:8000/v1
openstack endpoint create --region RegionOne cloudformation internal http://dev-controller:8000/v1
openstack endpoint create --region RegionOne cloudformation admin http://dev-controller:8000/v1

echo "Creating heat domains"
openstack domain create --description "Stack projects and users" heat
openstack user create --domain heat --password healthseq heat_domain_admin
openstack role add --domain heat --user heat_domain_admin admin

echo "Creating heat stack owner and user role"
openstack role create heat_stack_owner
openstack role add --project demo --user demo heat_stack_owner
openstack role create heat_stack_user

