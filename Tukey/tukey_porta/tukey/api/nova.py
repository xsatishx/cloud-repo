from collections import Sequence

from django.conf import settings

from openstack_dashboard.api import nova
from openstack_dashboard.api.base import Quota
from openstack_dashboard.api.nova import flavor_list
from openstack_dashboard.api.nova import novaclient
from openstack_dashboard.api.nova import server_list
from openstack_dashboard.api.nova import tenant_floating_ip_list
from openstack_dashboard.api.nova import tenant_quota_get
from horizon.utils.memoized import memoized

from tukey.cloud_attribute import get_cloud

from collections import OrderedDict

class NovaUsage(nova.NovaUsage):

    _attrs = ['start', 'server_usages', 'stop', 'tenant_id',
             'total_local_gb_usage', 'total_memory_mb_usage',
             'total_vcpus_usage', 'total_hours',
         'cloud_cores', 'cloud_du', 'cloud_ram', 'hadoop_jobs',
         'hadoop_hdfsdu'] + settings.USAGE_ATTRIBUTES.values()

    def get_summary(self):
        #TODO: find some way to make this ordered oh well it is not
        # going to happen :(
        return OrderedDict([('instances', self.total_active_instances),
                ('memory_mb', self.memory_mb),
                ('vcpus', getattr(self, "total_vcpus_usage", 0)),
                ('vcpu_hours', self.vcpu_hours),
                ('local_gb', self.local_gb),
                ('disk_gb_hours', self.disk_gb_hours),
                ('cloud_cores', getattr(self, "cloud_cores", -1)),
                ('cloud_du', getattr(self, "cloud_du", -1)),
                ('hadoop_hdfsdu', getattr(self, "hadoop_hdfsdu", -1)),
                ('hadoop_jobs', getattr(self, "hadoop_jobs", -1)),
                ('Cloud Core Hours', getattr(self, "cloud_cores", -1)),
                ('Cloud Disk Usage (GB)', getattr(self, "cloud_du", -1)),
                ('Cloud RAM Hours (GB Hours)', getattr(self, "cloud_ram", -1)),
                ('Hadoop Disk Usage (GB)', getattr(self, "hadoop_hdfsdu", -1)),
                ('Hadoop Job Hours', getattr(self, "hadoop_jobs", -1))]
            + [(key, getattr(self, value, -1)) for key, value in
            settings.USAGE_ATTRIBUTES.items()])


class QuotaSet2(Sequence):
    """
    Wrapper for client QuotaSet objects which turns the individual quotas
    into Quota objects for easier handling/iteration.

    `QuotaSet` objects support a mix of `list` and `dict` methods; you can use
    the bracket notiation (`qs["my_quota"] = 0`) to add new quota values, and
    use the `get` method to retrieve a specific quota, but otherwise it
    behaves much like a list or tuple, particularly in supporting iteration.
    """
    def __init__(self, apiresource=None):
        self.items = []
        if apiresource:
            for k, v in apiresource.items():
            #for k, v in apiresource._info.items():
                if k == 'id':
                    continue
                self[k] = v

    def __setitem__(self, k, v):
            v = int(v) if v is not None else v
            q = Quota(k, v)
            self.items.append(q)

    def __getitem__(self, index):
        return self.items[index]

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return repr(self.items)

    def get(self, key, default=None):
        match = [quota for quota in self.items if quota.name == key]
        return match.pop() if len(match) else Quota(key, default)


def default_quota_get(request, tenant_id):
    return cloud_quota(request, novaclient(request).quotas.defaults(tenant_id))

def tenant_quota_get(request, tenant_id):
    return cloud_quota(request, novaclient(request).quotas.get(tenant_id))


def cloud_quota(request, quotas):
    cloud = None
    if 'cloud' in request.GET:
        cloud = request.GET['cloud']
    elif 'cloud' in request.POST:
        cloud = request.POST['cloud']
    if cloud is not None:
        quotas = quotas._info[cloud]
        del(quotas['cloud'])
    else:
        # "sum" the quotas!
        # The attributes not to sum
        ignore = ['cloud', 'id']
        if hasattr(quotas, '_info'):
            clouds = quotas._info.keys()
            if 'cloud' in quotas._info[clouds[0]]:
                keys = []
                for cloud in clouds:
                    keys += quotas._info[cloud].keys()
                quotas = {key:
                    reduce(
                    lambda s, c: s + quotas._info[c][key] if key in quotas._info[c]
                    else 0, [0] + clouds) for key in keys if key not in ignore}

    return QuotaSet2(quotas)
