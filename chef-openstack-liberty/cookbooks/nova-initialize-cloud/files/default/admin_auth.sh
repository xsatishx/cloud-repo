#!/bin/bash
set -x
export credential_file="/root/admin_auth"
export USERNAME="admin"
export PASSWORD="${ADMIN_PASSWORD}"
export OS_AUTH_URL="http://norc.api.opensciencedatacloud.org:5000/v2.0/"
export EC2_URL="http://norc.api.opensciencedatacloud.org:8773/services/Cloud"

    echo "export OS_TENANT_NAME=$USERNAME" >> $credential_file
    echo "export OS_USERNAME=$USERNAME" >> $credential_file
    echo "export OS_PASSWORD=$PASSWORD" >> $credential_file
    echo "export OS_AUTH_URL=\"http://norc.api.opensciencedatacloud.org:5000/v2.0/\"" >> $credential_file

    #EUCA
    INFO_STRING="--os_username $USERNAME --os_password $PASSWORD --os_tenant_name $USERNAME"
    NOVA_INFO_STRING="--username $USERNAME --password $PASSWORD --tenant_name $USERNAME"

    CREDS=$(keystone $INFO_STRING ec2-credentials-create)

    EC2_URL=$(keystone $INFO_STRING catalog --service ec2 | awk '/ publicURL / { print $4 }')

    EC2_ACCESS_KEY=$(echo "$CREDS" | awk '/ access / { print $4 }')

    EC2_SECRET_KEY=$(echo "$CREDS" | awk '/ secret / { print $4 }')

    echo "export EC2_URL=$EC2_URL" >> $credential_file
    echo "export EC2_ACCESS_KEY=$EC2_ACCESS_KEY" >> $credential_file
    echo "export EC2_SECRET_KEY=$EC2_SECRET_KEY" >> $credential_file
