import logging

from django_openid_auth.views import (
    login_begin as old_login_begin,
    default_render_failure,
    REDIRECT_FIELD_NAME
)

from .models import UnregisteredUser
from django import forms
from django import shortcuts
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect
from django.utils.functional import curry
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt
from django_openid_auth import teams
from django_openid_auth.auth import OpenIDBackend
from django_openid_auth.exceptions import DjangoOpenIDException
from django_openid_auth.exceptions import MissingPhysicalMultiFactor
from django_openid_auth.forms import OpenIDLoginForm
from django_openid_auth.models import UserOpenID
from django_openid_auth.signals import openid_login_complete
from django_openid_auth.views import parse_openid_response, sanitise_redirect_url
from openid.consumer.consumer import SUCCESS
from openid.extensions import pape
from openstack_auth.backend import KeystoneBackend
from openstack_auth.exceptions import KeystoneAuthException
from openstack_dashboard.views import get_user_home
from simplejson.decoder import JSONDecodeError

import requests

LOG = logging.getLogger(__name__)


class OpenIDKeystoneBackend(KeystoneBackend):

    def __init__(self):
        self.openid_backend = OpenIDBackend()

    def authenticate(self, **kwargs):
        """Authenticate the user based on an OpenID response."""
        # Require that the OpenID response be passed in as a keyword
        # argument, to make sure we don't match the username/password
        # calling conventions of authenticate.

        openid_response = kwargs.get('openid_response')
        if openid_response is None:
            return None

        if openid_response.status != SUCCESS:
            return None

        user = None
        try:
            user_openid = UserOpenID.objects.get(
                claimed_id__exact=openid_response.identity_url)
        except UserOpenID.DoesNotExist:
            if getattr(settings, 'OPENID_CREATE_USERS', False):
                user = self.openid_backend.create_user_from_openid(
                        openid_response)
        else:
            user = user_openid.user

        if user is None:
            return None

        #if getattr(settings, 'OPENID_UPDATE_DETAILS_FROM_SREG', False):
        details = self.openid_backend._extract_user_details(openid_response)
        self.openid_backend.update_user_details(user, details, openid_response)

        if getattr(settings, 'OPENID_PHYSICAL_MULTIFACTOR_REQUIRED', False):
            pape_response = pape.Response.fromSuccessResponse(openid_response)
            if pape_response is None or \
               pape.AUTH_MULTI_FACTOR_PHYSICAL not in pape_response.auth_policies:
                raise MissingPhysicalMultiFactor()

        teams_response = teams.TeamsResponse.fromSuccessResponse(
            openid_response)
        if teams_response:
            self.openid_backend.update_groups_from_teams(user, teams_response)
            self.openid_backend.update_staff_status_from_teams(user,
                    teams_response)

        LOG.debug("email %s:", details['email'])

        try:
            user = super(OpenIDKeystoneBackend, self).authenticate(
                password=settings.TUKEY_PASSWORD,
                username='openid %s' % details['email'],
                auth_url=settings.OPENSTACK_KEYSTONE_URL,
                request=kwargs.get('request'))
            user.identifier = details['email']

        except KeystoneAuthException:
            return UnregisteredUser('OpenID', details['email'])

        return user


class ShibbolethOpenIDLoginForm(OpenIDLoginForm):

    def __init__(self, request, *args, **kwargs):

        super(ShibbolethOpenIDLoginForm, self).__init__(*args, **kwargs)
        LOG.debug("kwargs %s", kwargs)

        try:
            id_providers = {r["entityID"]:
                [n["value"] for n in r.get("DisplayNames",
                [{"value": r["entityID"], "lang": "en"}])
                    if n["lang"] == "en"][0]
                for r in requests.get((
                    "%s/Shibboleth.sso/DiscoFeed" % settings.SITE_URL)).json()}
        except JSONDecodeError:
            id_providers = {" ": "--- Error please refresh page ---"}

        try:
            extras = requests.get("%s/misc/idps.json" % settings.SITE_URL
                ).json()
            id_providers.update(extras)
        except JSONDecodeError:
            pass

        self.fields["entityid"] = forms.ChoiceField(
            label="Institution or Organization",
            choices=[(" ", "--- Select Your Institution ---")] + sorted(
                    [(entity, name) for entity, name in
                id_providers.items()], key=lambda tup: tup[1]), required=False)

        if "entityid_cookie" in request.COOKIES:
            LOG.debug("SETTING the entitty id to %s",
                request.COOKIES["entityid_cookie"])
            self.fields["entityid"].initial = request.COOKIES["entityid_cookie"]


@csrf_exempt
def pre_apply(request, template_name='openid/login.html',
                login_complete_view='openid:openid-complete',
                form_class=ShibbolethOpenIDLoginForm,
                render_failure=default_render_failure,
                redirect_field_name=REDIRECT_FIELD_NAME):

    if "openid_identifier" not in request.POST and "entityid" in request.POST:
        response = HttpResponseRedirect(
            "/Shibboleth.sso/Login?%s" % urlencode(
                {"entityID": request.POST["entityid"],
                    "target": "/apply/"}
            )
        )
        response.set_cookie("entityid_cookie", request.POST["entityid"])
        return response

    return old_login_begin(request,
        settings.ROOT_PATH + '/../tukey/templates/osdc/pre_apply.html',
        login_complete_view, curry(form_class, request), render_failure,
            redirect_field_name)


def login_begin(request, template_name='openid/login.html',
                login_complete_view='openid:openid-complete',
                form_class=ShibbolethOpenIDLoginForm,
                render_failure=default_render_failure,
                redirect_field_name=REDIRECT_FIELD_NAME):

    LOG.debug('new login begin')

    if request.user.is_authenticated():
        return shortcuts.redirect(get_user_home(request.user))

    if "openid_identifier" not in request.POST and "entityid" in request.POST:
        response = HttpResponseRedirect(
            "/Shibboleth.sso/Login?%s" % urlencode(
                {"entityID": request.POST["entityid"],
                    "target": request.POST.get("next", default="/project/")}
            )
        )
        response.set_cookie("entityid_cookie", request.POST["entityid"])

        return response

    return old_login_begin(request,
        settings.ROOT_PATH + '/../tukey/templates/osdc/openid_login.html',
        login_complete_view, curry(form_class, request), render_failure,
            redirect_field_name)


# replace login complete so that if the user is not
# authenticated this will send them to the page
# where they can register

def login_complete(request, redirect_field_name=REDIRECT_FIELD_NAME,
                   render_failure=None):
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    render_failure = render_failure or \
                     getattr(settings, 'OPENID_RENDER_FAILURE', None) or \
                     default_render_failure

    openid_response = parse_openid_response(request)
    if not openid_response:
        return HttpResponseRedirect(sanitise_redirect_url(redirect_to))

    if openid_response.status == SUCCESS:
        try:
            user = authenticate(openid_response=openid_response)
        except DjangoOpenIDException:
            return HttpResponseRedirect(sanitise_redirect_url(redirect_to))

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                response = HttpResponseRedirect(sanitise_redirect_url(redirect_to))

                # Notify any listeners that we successfully logged in.
                openid_login_complete.send(sender=UserOpenID, request=request,
                    user=user, openid_response=openid_response)

                return response
            else:
                if "next" in request.POST:
                    return HttpResponseRedirect(
                        "/Shibboleth.sso/Login?%s" % urlencode(
                                {"entityID": request.POST.get("entityid", ""),
                        "target": request.POST.get("next", default="/project/")}
                        )
                    )

                from tukey.webforms.views import osdc_apply
                return osdc_apply(request, user)

    return HttpResponseRedirect(sanitise_redirect_url(redirect_to))
