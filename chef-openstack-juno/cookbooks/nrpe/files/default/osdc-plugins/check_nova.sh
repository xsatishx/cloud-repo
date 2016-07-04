#!/bin/bash

CMD="$1"

if [ -z "$CMD" ]
then
    echo "WARNING: Usage:$0 $CMD "
    exit 1
fi


[ -e /etc/osdc_cloud_accounting/admin_auth ] && source /etc/osdc_cloud_accounting/admin_auth
[ -e /root/admin_auth ] && source /root/admin_auth
[ -e ~/admin_auth ] && source ~/admin_auth

        export OS_USERNAME=admin
        export OS_PASSWORD=uo9Xaich0ahz8ceCahW5
        export OS_TENANT_NAME=admin
        export OS_AUTH_URL=http://api-bionimbus-pdc.opensciencedatacloud.org:35357/v2.0
if [ -z "$OS_USERNAME" ] || [ -z "$OS_PASSWORD" ] || [ -z "$OS_TENANT_NAME" ] || [ -z "$OS_AUTH_URL" ]
then
    echo "WARNING: Nova Credentials not found"
    exit 1
fi


output=$(nova $CMD 2>&1 )
status_code="$?"

if [ "$status_code" == "0" ]
then
    echo "OK"
    exit 0
else
    echo "CRITICAL: $output"
    exit 2
fi
