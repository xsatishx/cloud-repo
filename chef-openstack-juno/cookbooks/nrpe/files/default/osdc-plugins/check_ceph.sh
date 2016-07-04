#!/bin/bash
cephstatus=$(sudo ceph -s 2>&1 |grep "HEALTH_" );
ceph_health=$( echo $cephstatus | perl -ne 'm|health\s+(\S+)\s+| && print "$1\n"' )


case ${ceph_health} in
        HEALTH_O*)
        echo "OK: ${cephstatus}"
        exit 0
        ;;
        HEALTH_W*)
        echo "WARNING: ${cephstatus}"
        exit 1
        ;;
        HEALTH_E*)
        echo "CRITICAL: ${cephstatus}"
        exit 2
        ;;
        *)
        echo "UNKNOWN: Ceph reports ${cephstatus}"
        exit 3
        ;;
esac
