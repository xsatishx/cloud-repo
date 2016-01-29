from openstack_dashboard.dashboards.project.access_and_security.views import IndexView as OldIndexView

from tukey.dashboards.project.access_and_security.keypairs.tables import KeypairsTable
from openstack_dashboard.dashboards.project.access_and_security.security_groups.tables import SecurityGroupsTable
from openstack_dashboard.dashboards.project.access_and_security.floating_ips.tables import FloatingIPsTable

from django.conf import settings

class IndexView(OldIndexView):
    if settings.DISABLE_SECURITY_GROUPS_AND_IPS:
        table_classes = (KeypairsTable,)
    else:
        table_classes = (KeypairsTable, SecurityGroupsTable, FloatingIPsTable)
