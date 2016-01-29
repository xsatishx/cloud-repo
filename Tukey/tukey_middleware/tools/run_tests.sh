#!/bin/bash
EXIT_ON_FAIL=${EXIT_ON_FAIL:-false}
SERVICE_WAIT=${SERVICE_WAIT:-5}

failed=0
passed=0

red='\e[0;31m'
green='\e[0;32m'
NC='\e[0m' # No Color

function run_test {
    echo "Running $1"
    if $1; then
        echo -e "${green}==================================${NC}"
        ((passed++))
    else
        echo $1
        echo -e "${red}==================================${NC}"

        ((failed++))
        if $EXIT_ON_FAIL; then
            exit 1
        fi
    fi
}

for mock in openstack euca euca_quota keystone; do
    python tukey_middleware/tests/services/${mock}_mock.py &> log/${mock}.log &
done

python tukey_middleware/server_test.py &> log/test_server.log &

sleep $SERVICE_WAIT;

for unit_test in api cloud_driver utils auth api_driver; do
    run_test "python -m tukey_middleware.tests.test_$unit_test"
done

# run the client tests
source tools/eucarc

for sub_command in list image-list keypair-list flavor-list; do
    run_test "nova $sub_command"
done

run_test "nova keypair-add test_openstack-test"
run_test "nova keypair-delete test_openstack-test"
run_test "nova delete dae9f67d-7c6d-499f-9df0-0c6bee58400b"
run_test "nova delete 00491708-2c00-0000-0000-000000000000"
run_test "nova boot --flavor 1 --image 0a97a0b3-ee4f-4041-aa0b-b7febb4d5072 test_openstack-test"
run_test "nova boot --flavor m1.small --image 00938d13-6d00-0000-0000-000000000000  test_cloud-test"

for mock in openstack euca euca_quota keystone; do
    pkill -f python\ tukey_middleware/tests/services/${mock}_mock.py
done

pkill -f python\ tukey_middleware/server_test.py

if [ "$failed" -ne "0" ]; then
    echo -e "${red}==================================${NC}"
fi

echo "Ran $((passed + failed)) tests. $passed passed.  $failed failed"
