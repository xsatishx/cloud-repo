crudini --set /etc/keystone/keystone.conf DEFAULT admin_token healthseq
crudini --set /etc/keystone/keystone.conf DEFAULT verbose True
crudini --set /etc/keystone/keystone.conf database connection mysql+pymysql://keystone:healthseq@dev-controller/keystone
crudini --set /etc/keystone/keystone.conf memcache servers localhost:11211
crudini --set /etc/keystone/keystone.conf token provider uuid
crudini --set /etc/keystone/keystone.conf token driver memcache
crudini --set /etc/keystone/keystone.conf revoke driver sql
