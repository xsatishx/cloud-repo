import sys
from django.conf import settings
from tukey.cloud_attribute import get_cloud

from django import forms
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from horizon import tables, conf
# Explicitly get Row class from base.py in order to subclass it. May not need this because UpdateRow subclasses it, and UpdateRow is imported here.
from horizon.tables.base import Cell, Row as OldRow

from openstack_dashboard.dashboards.project.images_and_snapshots.images.tables import (
    ImagesTable as OldImagesTable,
    LaunchImage as OldLaunchImage)

from openstack_dashboard.dashboards.project.images_and_snapshots.images.tables import EditImage, CreateImage, DeleteImage
from openstack_dashboard.dashboards.project.images_and_snapshots.images.tables import UpdateRow as OldUpdateRow

from tukey.cloud_attribute import get_cloud

STRING_SEPARATOR = "__"

class UpdateRow(OldUpdateRow):

    def load_cells(self, datum=None):
        """
        Load the row's data (either provided at initialization or as an
        argument to this function), initiailize all the cells contained
        by this row, and set the appropriate row properties which require
        the row's data to be determined.

        This function is called automatically by
        :meth:`~horizon.tables.Row.__init__` if the ``datum`` argument is
        provided. However, by not providing the data during initialization
        this function allows for the possibility of a two-step loading
        pattern when you need a row instance but don't yet have the data
        available.
        """
        # Compile all the cells on instantiation.
        table = self.table
        if datum:
            self.datum = datum
        else:
            datum = self.datum
        cells = []
        for column in table.columns.values():
            if column.auto == "multi_select":
                widget = forms.CheckboxInput(check_test=False)
                # Convert value to string to avoid accidental type conversion
                data = widget.render('object_ids',
                                     unicode(table.get_object_id(datum)))
                table._data_cache[column][table.get_object_id(datum)] = data
            elif column.auto == "actions":
                data = table.render_row_actions(datum)
                table._data_cache[column][table.get_object_id(datum)] = data
            else:
                data = column.get_data(datum)
            cell = Cell(datum, data, column, self)
            cells.append((column.name or column.auto, cell))
        self.cells = SortedDict(cells)

        if self.ajax:
            interval = conf.HORIZON_CONFIG['ajax_poll_interval']
            self.attrs['data-update-interval'] = interval
            self.attrs['data-update-url'] = self.get_ajax_update_url()
            self.classes.append("ajax-update")

        # Add class of image's cloud name
        image_cloud = get_cloud(datum)
        self.classes.append(image_cloud.lower())

        # Add the row's status class and id to the attributes to be rendered.
        self.classes.append(self.status_class)
        id_vals = {"table": self.table.name,
                   "sep": STRING_SEPARATOR,
                   "id": table.get_object_id(datum)}
        self.id = "%(table)s%(sep)srow%(sep)s%(id)s" % id_vals
        self.attrs['id'] = self.id

class LaunchImage(OldLaunchImage):

    def get_link_url(self, datum):
        base_url = reverse(self.url)
        params = urlencode({"source_type": "image_id",
                "cloud": get_cloud(datum),
                            "source_id": self.table.get_object_id(datum)})
        return "?".join([base_url, params])

class LaunchCluster(tables.LinkAction):
    name = "launch_cluster"
    verbose_name = _("Launch Cluster")
    url = "horizon:project:instances:launch_cluster"
    classes = ("btn-launch", "ajax-modal")

    def get_link_url(self, datum):
        base_url = reverse(self.url)
        params = urlencode({"source_type": "image_id",
                "cloud": get_cloud(datum),
                            "source_id": self.table.get_object_id(datum)})
        return "?".join([base_url, params])

    def allowed(self, request, image):
        return get_cloud(image).lower() in settings.CLOUD_FUNCTIONS['launch_cluster']

class ImageFilterAction(tables.FilterAction):

    def filter(self, table, instances, filter_string):
        q = filter_string.lower()
        return [instance for instance in instances if q in instance.name.lower()]

class ImagesTable(OldImagesTable):
    cloud = tables.Column(get_cloud, verbose_name=_("Cloud"))

    class Meta:
        name = "images"
        row_class = UpdateRow
        status_columns = ["status"]
        verbose_name = _("Images")
        table_actions = (CreateImage, DeleteImage, ImageFilterAction)
        row_actions = (LaunchImage, LaunchCluster, EditImage, DeleteImage,)
        pagination_param = "image_marker"
