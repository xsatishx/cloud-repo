from django.utils.translation import ugettext_lazy as _

from horizon import tables
from openstack_dashboard.dashboards.project.access_and_security.keypairs.tables import KeypairsTable as OldKeypairsTable

from tukey.cloud_attribute import get_cloud, get_cloud_id

class KeypairsTable(OldKeypairsTable):

    # Thie should be somewhere else but I just don't know where
    # mgreenway
    cloud = tables.Column(get_cloud, verbose_name=_("Resource"))
    #end modified section mgreenway

    def get_object_id(self, keypair):
        return get_cloud_id(keypair) + '-' + keypair.name

    Meta = OldKeypairsTable.Meta
