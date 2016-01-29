from django.utils.translation import ugettext_lazy as _

from horizon import exceptions

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.images_and_snapshots.views import IndexView as OldIndexView

from tukey.dashboards.project.images_and_snapshots.images.tables import ImagesTable
from tukey.dashboards.project.images_and_snapshots.snapshots.tables import UserSnapshotsTable, OtherSnapshotsTable
from openstack_dashboard.dashboards.project.images_and_snapshots.volume_snapshots.tables import VolumeSnapshotsTable

#from horizon.dashboards.nova.images_and_snapshots.images.tables import ImagesTable
#from horizon.dashboards.nova.images_and_snapshots.snapshots.tables import SnapshotsTable

class IndexView(OldIndexView):

    table_classes = (ImagesTable, UserSnapshotsTable, OtherSnapshotsTable, VolumeSnapshotsTable)

    def get_usersnapshots_data(self):
        req = self.request
        marker = req.GET.get(UserSnapshotsTable._meta.pagination_param, None)
        try:
            usersnaps, self._more_snapshots = api.snapshot_list_detailed(
                                                               req,
                                                               marker = marker,
                                                               extra_filters = {"owner" : req.user.tenant_id}
                                                               )
        except:
            usersnaps = []
            exceptions.handle(req, _("Unable to retrieve user-owned snapshots."))
        return usersnaps

    def get_othersnapshots_data(self):  
        req = self.request
        marker = req.GET.get(OtherSnapshotsTable._meta.pagination_param, None)
        try:
            othersnaps, self._more_snapshots = api.snapshot_list_detailed(
                                                                req,
                                                                marker = marker
                                                                )
            othersnaps = [im for im in othersnaps
                if im.container_format not in ['aki', 'ari'] and im.properties.get("image_type") == 'snapshot']
        except:
            othersnaps = []
            exceptions.handle(req, _("Unable to retrieve list of all snapshots."))
        return othersnaps
