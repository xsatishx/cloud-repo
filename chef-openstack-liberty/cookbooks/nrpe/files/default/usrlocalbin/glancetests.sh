#!/bin/bash
source /etc/osdc_cloud_accounting/admin_auth
/usr/bin/time -f "%e,$(date +%s)" --output=/usr/local/var/log/glancetime -- glance image-download b4437b8e-a26a-4cbd-bb4f-5b4a7ef6ef31 > /dev/null
