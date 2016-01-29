import re

from django import shortcuts
from django.core import validators
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard.dashboards.project.access_and_security.keypairs.forms import (
    CreateKeypair as OldCreateKeypair,
    ImportKeypair as OldImportKeypair)

from tukey.cloud_attribute import cloud_details, has_function

from openstack_dashboard import api
from horizon import exceptions
from horizon import forms
from horizon import messages


NEW_LINES = re.compile(r"\r|\n")


def get_resources(function_name, user):
    return ((key, _(value)) for
        (key, value) in cloud_details(user).items() if
        has_function(function_name, key))


class CreateKeypair(OldCreateKeypair):
    # Initial added by Alex.
    cloud = forms.ChoiceField(label=_("Resource"),required=True, initial="all")

    def __init__(self, request, *args, **kwargs):

        self.base_fields['cloud'].choices = get_resources('create_keypair',
            request.user)

        # Important point here:
        # when the super class was me it caused recursion depth exceed
        super(OldCreateKeypair, self).__init__(request, *args, **kwargs)


class ImportKeypair(OldImportKeypair):
    # Initial added by Alex.
    cloud = forms.ChoiceField(label=_("Resource"),required=True, initial="all")

    def __init__(self, request, *args, **kwargs):

        self.base_fields['cloud'].choices = get_resources('import_keypair',
            request.user)

        super(OldImportKeypair, self).__init__(request, *args, **kwargs)


    def handle(self, request, data):
        try:
            # Remove any new lines in the public key
            data['public_key'] = NEW_LINES.sub("", data['public_key'])
            keypair = api.keypair_import(request,
                                         data['cloud'] + '-' + data['name'],
                                         data['public_key'])
            messages.success(request, _('Successfully imported public key: %s')
                                       % data['name'])
            return keypair
        except:
            exceptions.handle(request, ignore=True)
            self.api_error(_('Unable to import keypair.'))
            return False
