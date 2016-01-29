from django.conf import settings
from django.utils.text import normalize_newlines
from django.utils.translation import ugettext as _

from horizon import exceptions
from horizon import forms
from horizon import workflows
from openstack_dashboard import api

from tukey.cloud_attribute import get_cloud

from openstack_dashboard.dashboards.project.instances.workflows import(
    LaunchInstance as OldLaunchInstance,
    PostCreationStep,
    SelectProjectUser,
    SetAccessControls,
    SetAccessControlsAction,
    SetInstanceDetails,
    SetInstanceDetailsAction)


class SetClusterDetailsAction(SetInstanceDetailsAction):
    SOURCE_TYPE_CHOICES = (
        ("image_id", _("Image")),
        ("instance_snapshot_id", _("Snapshot")),
    )
    source_type = forms.ChoiceField(label=_("Compute Node Source"),
                                    choices=SOURCE_TYPE_CHOICES)

    image_id = forms.ChoiceField(label=_("Image"), required=False)
    instance_snapshot_id = forms.ChoiceField(label=_("Instance Snapshot"),
                                             required=False)

    name = forms.CharField(initial='none', widget=forms.HiddenInput())
    flavor = forms.ChoiceField(label=_("Flavor"),
                               help_text=_("Size of compute nodes to launch."))

    headnode_image_id = forms.ChoiceField(label=_("Headnode Image"),
                               help_text=_("Image for headnode"))

    headnode_flavor = forms.ChoiceField(label=_("Headnode Flavor"),
                               help_text=_("Size of headnode to launch."))

    count = forms.IntegerField(label=_("Compute Node Count"),
                               min_value=1,
                               initial=1,
                               help_text=_("Number of compute nodes to launch."))

    cloud = forms.CharField(max_length=80, label=_("Cloud Name"))
    cloud.widget.attrs['readonly'] = True
    #name.widget.attrs['visible'] = False


    class Meta:
        name = _("Details")
        help_text_template = (settings.ROOT_PATH + "/../tukey/templates/project"
                            "/instances/_launch_cluster_details_help.html")

class SetClusterDetails(SetInstanceDetails):
    action_class = SetClusterDetailsAction
    contributes = ("source_type", "source_id", "count", "flavor",
            "headnode_flavor", "headnode_image_id", "cloud")

    def prepare_action_context(self, request, context):
        if 'source_type' in context and 'source_id' in context:
            context[context['source_type']] = context['source_id']
            context['headnode_image_id'] = context['source_id']
        return context


class LaunchInstance(OldLaunchInstance):

    default_steps = (SelectProjectUser,
                     SetInstanceDetails,
                     SetAccessControls,
                     #VolumeOptions,
                     PostCreationStep)


    def handle(self, request, context):
        custom_script = context.get('customization_script', '')

        # Determine volume mapping options
        if context.get('volume_type', None):
            if(context['delete_on_terminate']):
                del_on_terminate = 1
            else:
                del_on_terminate = 0
            mapping_opts = ("%s::%s"
                            % (context['volume_id'], del_on_terminate))
            dev_mapping = {context['device_name']: mapping_opts}
        else:
            dev_mapping = None

        netids = context.get('network_id', None)
        if netids:
            nics = [{"net-id": netid, "v4-fixed-ip": ""}
                    for netid in netids]
        else:
            nics = None

        try:
            api.nova.server_create(request,
                                   context['cloud'].lower() + '-' + context['name'],
                                   context['source_id'],
                                   context['flavor'],
                                   context['keypair_id'],
                                   normalize_newlines(custom_script),
                                   context['security_group_ids'],
                                   dev_mapping,
                                   nics=nics,
                                   instance_count=int(context['count']))
            return True
        except:
            exceptions.handle(request)
            return False



SetInstanceDetails.contributes = ("source_type", "source_id", "name",
    "count", "flavor", "cloud")



def populate_image_id_choices(self, request, context):

    images = self._get_available_images(request, context)

    if 'cloud' in request.GET:
        cloud = request.GET['cloud']

        if cloud.lower() not in settings.CLOUD_FUNCTIONS['launch_multiple']:
            self.fields['count'].widget.attrs['readonly'] = True

        if cloud.lower() not in settings.CLOUD_FUNCTIONS['namable_servers']:
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['name'].widget.attrs['value'] = 'Feature not supported.'

        choices = [(image.id, image.name) for image in images
            if image.properties.get("image_type", '') != "snapshot"
            and (get_cloud(image) == cloud)]
    else:
        choices = [(image.id, image.name) for image in images
            if image.properties.get("image_type", '') != "snapshot"]
    if choices:
        choices.insert(0, ("", _("Select Image")))
    else:
        choices.insert(0, ("", _("No images available.")))
    return choices


def populate_instance_snapshot_id_choices(self, request, context):
    images = self._get_available_images(request, context)

    if 'cloud' in request.GET:
        cloud = request.GET['cloud']

        if cloud.lower() not in settings.CLOUD_FUNCTIONS['launch_multiple']:
            self.fields['count'].widget.attrs['readonly'] = True

        if cloud.lower() not in settings.CLOUD_FUNCTIONS['namable_servers']:
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['name'].widget.attrs['value'] = 'Feature not supported.'

        choices = [(image.id, image.name) for image in images
            if image.properties.get("image_type", '') == "snapshot"
            and (get_cloud(image) == cloud)]
    else:
        choices = [(image.id, image.name)
               for image in images
               if image.properties.get("image_type", '') == "snapshot"]
    if choices:
        choices.insert(0, ("", _("Select Instance Snapshot")))
    else:
        choices.insert(0, ("", _("No snapshots available.")))
    return choices


def populate_headnode_image_id_choices(self, request, context):
    images = self._get_available_images(request, context)

    if 'cloud' in request.GET:
        cloud = request.GET['cloud']

        if cloud.lower() not in settings.CLOUD_FUNCTIONS['launch_multiple']:
            self.fields['count'].widget.attrs['readonly'] = True

        if cloud.lower() not in settings.CLOUD_FUNCTIONS['namable_servers']:
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['name'].widget.attrs['value'] = 'Feature not supported.'

        choices = [(image.id, image.name) for image in images
            if (get_cloud(image) == cloud)]
    else:
        choices = [(image.id, image.name) for image in images]
    if choices:
        choices.insert(0, ("", _("Select Snapshot/Image")))
    else:
        choices.insert(0, ("", _("No images available.")))
    return choices


def populate_flavor_choices(self, request, context):
    try:
        flavors = api.nova.flavor_list(request)

        if 'cloud' in request.GET:
            cloud = request.GET['cloud']
            flavor_list = [(flavor.id, "%s" % flavor.name)
                       for flavor in flavors
           if get_cloud(flavor) == cloud]
        else:
            flavor_list = [(flavor.id, "%s" % flavor.name)
                       for flavor in flavors]
    except:
        flavor_list = []
        exceptions.handle(request,
                          _('Unable to retrieve instance flavors.'))
    return sorted(flavor_list)


def populate_headnode_flavor_choices(self, request, context):
    ''' Make sure that medium is first '''

    choices = populate_flavor_choices(self, request, context)
    first = 'm1.medium'
    return ([f for f in choices if f[1] == first] +
            [f for f in choices if f[1] != first])

SetInstanceDetails.action_class.populate_image_id_choices = populate_image_id_choices
SetInstanceDetails.action_class.populate_instance_snapshot_id_choices = populate_instance_snapshot_id_choices
SetInstanceDetails.action_class.populate_flavor_choices = populate_flavor_choices
SetInstanceDetails.action_class.populate_headnode_flavor_choices = populate_headnode_flavor_choices
SetInstanceDetails.action_class.populate_headnode_image_id_choices = populate_headnode_image_id_choices


SetAccessControls.depends_on = ("project_id", "user_id", "cloud")


def cloud_filter(self, elements, field_name, function, request, context):
    if 'cloud' in request.GET:
        context['cloud'] = request.GET['cloud']
    if 'cloud' in context:
        if context['cloud'].lower() not in settings.CLOUD_FUNCTIONS[function]:
            self.fields[field_name].widget = forms.HiddenInput()
        else:
            self.fields[field_name].required = True
        cloud = context['cloud']
        element_list = [(kp.name, kp.name) for kp in elements
                if get_cloud(kp) == cloud]

    return element_list


def populate_keypair_choices(self, request, context):
    try:
        keypairs = api.nova.keypair_list(request)
        keypair_list = cloud_filter(self, keypairs, 'keypair', 'instance_keys', request,
            context)
    # fix this
    except:
        keypair_list = []
        exceptions.handle(request,
                          _('Unable to retrieve keypairs.'))
    if keypair_list:
        keypair_list.insert(0, ("", _("Select a keypair")))
    else:
        keypair_list = (("", _("No keypairs available.")),)
    return keypair_list


SetAccessControlsAction.populate_keypair_choices = populate_keypair_choices


def populate_groups_choices(self, request, context):
    try:
        groups = api.nova.security_group_list(request)
        security_group_list = cloud_filter(self, groups, 'groups', 'security_groups', request,
                context)
    except:
        exceptions.handle(request,
                          _('Unable to retrieve list of security groups'))
        security_group_list = []
    return security_group_list


SetAccessControlsAction.populate_groups_choices = populate_groups_choices


class LaunchCluster(workflows.Workflow):
    slug = "launch_cluster"
    name = _("Launch Cluster")
    finalize_button_name = _("Launch Cluster")
    success_message = _("Cluster launching. Refresh the page to monitor node "
                     "status while the cluster servers initialize.")
    failure_message = _("Unable to launch cluster")
    success_url = "horizon:project:instances:index"
    default_steps = (SelectProjectUser,
                     SetClusterDetails,
                     SetAccessControls,
                     #SetNetwork,
                     #VolumeOptions,
                     PostCreationStep)

    def format_status_message(self, message):
        return message
#        name = self.context.get('name', 'unknown instance')
#        count = self.context.get('count', 1)
#        return ("%s Cluster is launching. Please refresh the page to monitor node status"
#            " as the cluster servers are initialized.") % message
#        if int(count) > 1:
#            return message % {"count": _("%s nodes") % count}
#        else:
#            return message % {"count": _("1 compute node")}

    def handle(self, request, context):
        custom_script = context.get('customization_script', '')

        # Determine volume mapping options
        if context.get('volume_type', None):
            if(context['delete_on_terminate']):
                del_on_terminate = 1
            else:
                del_on_terminate = 0
            mapping_opts = ("%s::%s"
                            % (context['volume_id'], del_on_terminate))
            dev_mapping = {context['device_name']: mapping_opts}
        else:
            dev_mapping = None

        netids = context.get('network_id', None)
        if netids:
            nics = [{"net-id": netid, "v4-fixed-ip": ""}
                    for netid in netids]
        else:
            nics = None
        try:
            # note the bottom part doesn't work just wishfull thinking
            api.nova.novaclient(request).servers.create(
                    "cluster%s-%s-%s" % (context['cloud'].lower(),
                        context['headnode_flavor'],
                        context['headnode_image_id']),
                    context['source_id'],
                    context['flavor'],
                    key_name=context['keypair_id'],
                    userdata=normalize_newlines(custom_script),
                    security_groups=context['security_group_ids'],
                    block_device_mapping=dev_mapping,
                    nics=nics,
                    min_count=int(context['count']),
                    headnode_flavor=context['headnode_flavor'])
            return True
        except:
            exceptions.handle(request)
            return False

