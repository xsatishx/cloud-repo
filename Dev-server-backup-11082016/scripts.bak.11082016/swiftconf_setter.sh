crudini --set /etc/swift/proxy-server.conf DEFAULT bind_port 8080

crudini --set /etc/swift/proxy-server.conf DEFAULT user swift
crudini --set /etc/swift/proxy-server.conf DEFAULT swift_dir /etc/swift
crudini --set /etc/swift/proxy-server.conf pipeline:main pipeline "catch_errors gatekeeper healthcheck proxy-logging cache container_sync bulk ratelimit authtoken keystoneauth container-quotas account-quotas slo dlo versioned_writes proxy-logging proxy-server"

crudini --set /etc/swift/proxy-server.conf app:proxy-server use egg:swift#proxy
crudini --set /etc/swift/proxy-server.conf app:proxy-server account_autocreate true

crudini --set /etc/swift/proxy-server.conf filter:keystoneauth use egg:swift#keystoneauth
crudini --set /etc/swift/proxy-server.conf filter:keystoneauth operator_roles "admin,user"
crudini --del /etc/swift/proxy-server.conf filter:authtoken
crudini --set /etc/swift/proxy-server.conf filter:authtoken paste.filter_factory keystonemiddleware.auth_token:filter_factory
crudini --set /etc/swift/proxy-server.conf filter:authtoken auth_uri http://dev-controller:5000 
crudini --set /etc/swift/proxy-server.conf filter:authtoken auth_url http://dev-controller:35357
crudini --set /etc/swift/proxy-server.conf filter:authtoken auth_plugin password
crudini --set /etc/swift/proxy-server.conf filter:authtoken project_domain_id default
crudini --set /etc/swift/proxy-server.conf filter:authtoken user_domain_id default
crudini --set /etc/swift/proxy-server.conf filter:authtoken project_name service
crudini --set /etc/swift/proxy-server.conf filter:authtoken username swift
crudini --set /etc/swift/proxy-server.conf filter:authtoken password healthseq
crudini --set /etc/swift/proxy-server.conf filter:authtoken delay_auth_decision true
crudini --set /etc/swift/proxy-server.conf filter:cache use egg:swift#memcache
crudini --set /etc/swift/proxy-server.conf filter:cache memcache_servers 10.0.2.13:11211
