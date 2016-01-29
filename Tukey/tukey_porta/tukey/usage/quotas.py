from collections import defaultdict
import itertools

from horizon import exceptions
from horizon.utils.memoized import memoized

from openstack_dashboard.api import nova, cinder
from openstack_dashboard.api.base import is_service_enabled, QuotaSet

from openstack_dashboard.usage.quotas import QuotaUsage, get_tenant_quota_data

from tukey.cloud_attribute import get_cloud

@memoized
def tenant_quota_usages(request):

    cloud = None
    if 'cloud' in request.GET:
        cloud = request.GET['cloud']
    elif 'cloud' in request.POST:
        cloud = request.POST['cloud']

    # Get our quotas and construct our usage object.
    disabled_quotas = []
    if not is_service_enabled(request, 'volume'):
        disabled_quotas.extend(['volumes', 'gigabytes'])

    usages = QuotaUsage()
    for quota in get_tenant_quota_data(request, disabled_quotas):
        usages.add_quota(quota)

    # Get our usages.
    floating_ips = nova.tenant_floating_ip_list(request)
    #flavors = dict([(f.id, f) for f in nova.flavor_list(request) if limit_by_cloud(f) ])
    flavors = dict([(f.id, f) for f in nova.flavor_list(request) ])

    instances = nova.server_list(request)
    if cloud is not None:
        instances = [instance for instance in instances 
            if get_cloud(instance) == cloud]

    # Fetch deleted flavors if necessary.
    missing_flavors = [instance.flavor['id'] for instance in instances
                       if instance.flavor['id'] not in flavors]
    for missing in missing_flavors:
        if missing not in flavors:
            try:
                flavors[missing] = nova.flavor_get(request, missing)
            except:
                flavors[missing] = {}
                exceptions.handle(request, ignore=True)

    usages.tally('instances', len(instances))
    usages.tally('floating_ips', len(floating_ips))

    if 'volumes' not in disabled_quotas:
        volumes = cinder.volume_list(request)
        usages.tally('gigabytes', sum([int(v.size) for v in volumes]))
        usages.tally('volumes', len(volumes))

    # Sum our usage based on the flavors of the instances.
    for flavor in [flavors[instance.flavor['id']] for instance in instances]:
        usages.tally('cores', getattr(flavor, 'vcpus', None))
        usages.tally('ram', getattr(flavor, 'ram', None))

    # Initialise the tally if no instances have been launched yet
    if len(instances) == 0:
        usages.tally('cores', 0)
        usages.tally('ram', 0)

    return usages

