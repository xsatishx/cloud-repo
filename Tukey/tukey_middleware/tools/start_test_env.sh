#!/bin/bash

python tukey_middleware/tests/services/openstack_mock.py &> log/openstack.log &
python tukey_middleware/tests/services/euca_mock.py &> log/euca.log &
python tukey_middleware/tests/services/euca_quota_mock.py &> log/euca_quota.log &

python tukey_middleware/tests/services/keystone_mock.py &> log/keystone.log &
python tukey_middleware/server_test.py &> log/test_server.log &
