#!/bin/bash
CHECKS=$(md5sum --quiet -c /usr/local/share/osdc-plugins/check_ldap.md5)

if [ "$CHECKS" == "" ]
then
    echo "LDAP config in place - OK"
    exit 0
fi

echo "LDAP config altered - ERROR - $CHECKS"
exit 2
