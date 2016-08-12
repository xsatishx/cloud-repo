#Create Service
echo "Creating keystone Service"
openstack service create --name keystone --description "OpenStack Identity" identity

echo "Creating keystone endpoints"
openstack endpoint create --region RegionOne identity public http://dev-controller:5000/v2.0
openstack endpoint create --region RegionOne identity internal http://dev-controller:5000/v2.0
openstack endpoint create --region RegionOne identity admin http://dev-controller:35357/v2.0
#Create projects, users and roles

echo "Creating keystone admin project"
openstack project create --domain default  --description "Admin Project" admin

echo "Creating keystone admin user and role"
openstack user create --domain default --password healthseq admin
openstack role create admin 
openstack role add --project admin --user admin admin

echo "Creating service project"
openstack project create --domain default  --description "Service Project" service

echo "Creating keystone demo projects,users and role"

openstack project create --domain default  --description "Demo Project" demo
openstack user create --domain default  --password healthseq demo
openstack role create user  
openstack role add --project demo --user demo user
