#!/bin/bash
pkill -f python\ tukey_middleware/tests/services/openstack_mock.py
pkill -f python\ tukey_middleware/tests/services/euca_mock.py
pkill -f python\ tukey_middleware/tests/services/euca_quota_mock.py
pkill -f python\ tukey_middleware/tests/services/keystone_mock.py
pkill -f python\ tukey_middleware/server_test.py

