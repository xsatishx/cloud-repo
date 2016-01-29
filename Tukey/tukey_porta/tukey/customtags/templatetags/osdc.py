# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import

from django import template
from django.utils.translation import ugettext as _
from django.utils.datastructures import SortedDict

from horizon.base import Horizon


register = template.Library()

@register.inclusion_tag('osdc/_osdc_console_list.html', takes_context=True)
def osdc_console_nav(context):
    """ Generates sub-navigation entries for the current dashboard. """
    if 'request' not in context:
        return {}

    dashboard = context['request'].horizon['dashboard']
    if dashboard is None:
        return {}

    panel_groups = dashboard.get_panel_groups()
    non_empty_groups = []

    for group in panel_groups.values():
        allowed_panels = []
        for panel in group:
            if callable(panel.nav) and panel.nav(context):
                allowed_panels.append(panel)
            elif not callable(panel.nav) and panel.nav:
                allowed_panels.append(panel)
        if allowed_panels:
            non_empty_groups.append((group.name, allowed_panels))

    return {'components': SortedDict(non_empty_groups),
            'user': context['request'].user,
            'current': context['request'].horizon['panel'].slug,
            'request': context['request']}
