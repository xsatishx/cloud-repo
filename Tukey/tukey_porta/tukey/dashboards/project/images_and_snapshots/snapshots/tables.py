from django.conf import settings
from tukey.cloud_attribute import get_cloud


from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from horizon import tables

from openstack_dashboard.dashboards.project.images_and_snapshots.snapshots.tables import (
    SnapshotsTable as OldSnapshotsTable,
    LaunchSnapshot as OldLaunchSnapshot,
    DeleteSnapshot)

from openstack_dashboard.dashboards.project.images_and_snapshots.snapshots.tables import EditImage, UpdateRow

from tukey.cloud_attribute import get_cloud

#from tukey.dashboards.project.images_and_snapshots.images.tables import LaunchCluster


class LaunchSnapshot(OldLaunchSnapshot):

    def get_link_url(self, datum):
        base_url = reverse(self.url)
        params = urlencode({"source_type": "instance_snapshot_id",
                "cloud": get_cloud(datum),
                            "source_id": self.table.get_object_id(datum)})
        return "?".join([base_url, params])


class ImageFilterAction(tables.FilterAction):

    def filter(self, table, instances, filter_string):
        q = filter_string.lower()
        return [instance for instance in instances if q in instance.name.lower()]


class LaunchCluster(tables.LinkAction):
    name = "launch_cluster"
    verbose_name = _("Launch Cluster")
    url = "horizon:project:instances:launch_cluster"
    classes = ("btn-launch", "ajax-modal")

    def get_link_url(self, datum):
        base_url = reverse(self.url)
        params = urlencode({"source_type": "instance_snapshot_id",
                "cloud": get_cloud(datum),
                            "source_id": self.table.get_object_id(datum)})
        return "?".join([base_url, params])

    def allowed(self, request, image):
        return get_cloud(image).lower() in settings.CLOUD_FUNCTIONS['launch_cluster'] and image.status in ("active",)


# Tried to subclass this from OtherSnapshotsTable below to avoid repeating code, but that eliminates functionality.
class UserSnapshotsTable(OldSnapshotsTable):
    cloud = tables.Column(get_cloud, verbose_name=_("Cloud"))

    class Meta:
        name = "usersnapshots"
        verbose_name = _("User Snapshots")
        table_actions = (DeleteSnapshot, ImageFilterAction)
        row_actions = (LaunchSnapshot, LaunchCluster, EditImage, DeleteSnapshot)
        pagination_param = "snapshot_marker"
        row_class = UpdateRow
        status_columns = ["status"]


class OtherSnapshotsTable(OldSnapshotsTable):
    cloud = tables.Column(get_cloud, verbose_name=_("Cloud"))

    class Meta:
        name = "othersnapshots"
        verbose_name = _("All Snapshots")
        table_actions = (DeleteSnapshot, ImageFilterAction)
        row_actions = (LaunchSnapshot, LaunchCluster, EditImage, DeleteSnapshot)
        pagination_param = "snapshot_marker"
        row_class = UpdateRow
        status_columns = ["status"]
