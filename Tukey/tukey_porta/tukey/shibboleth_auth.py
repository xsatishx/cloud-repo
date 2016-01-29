import logging

from .models import UnregisteredUser
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.signals import user_logged_in
from keystoneclient import exceptions as keystone_exceptions
from openstack_auth import utils
from openstack_auth.backend import KeystoneBackend
from openstack_auth.exceptions import KeystoneAuthException
from openstack_auth.user import set_session_from_user

LOG = logging.getLogger(__name__)

def get_user(request):

    try:
        user_id = request.session[auth.SESSION_KEY]
        backend_path = request.session[auth.BACKEND_SESSION_KEY]
        backend = auth.load_backend(backend_path)
        backend.request = request
        user = backend.get_user(user_id) or AnonymousUser()

        request.session.set_expiry(settings.SESSION_TIMEOUT)


    except KeyError:
        shib_header = None


        for possible_header in settings.SHIB_HEADERS:
            if possible_header in request.META and request.META.get(
                possible_header):
                shib_header = possible_header
                break

        if shib_header is not None:
            LOG.debug("Shibboleth header is set")
            LOG.debug("username %s", request.META.get(shib_header))
            keystone = KeystoneBackend()
            try:
                user = keystone.authenticate(password=settings.TUKEY_PASSWORD,
                    username="shibboleth %s" % request.META.get(shib_header),
                    auth_url=settings.OPENSTACK_KEYSTONE_URL,
                    request=request)
                user.backend = 'openstack_auth.backend.KeystoneBackend'
                user.identifier = request.META.get(shib_header)
                login(request, user)
            except (keystone_exceptions.Unauthorized, KeystoneAuthException):
                user = UnregisteredUser('Shibboleth',
                    request.META.get(shib_header))


        else:
            user = AnonymousUser()
    return user


def login(request, user):
    if user is None:
        user = request.user
    # TODO: It would be nice to support different login methods, like signed cookies.
    if auth.SESSION_KEY in request.session:
        if request.session[auth.SESSION_KEY] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session[auth.SESSION_KEY] = user.id
    request.session[auth.BACKEND_SESSION_KEY] = user.backend

    set_session_from_user(request, user)

    if hasattr(request, 'user'):
        request.user = user

    user_logged_in.send(sender=user.__class__, request=request, user=user)


def patch_openstack_middleware_get_user():

    auth.login = login

    utils.get_user = get_user

    from django_openid_auth import auth as django_openid_auth
    from tukey.openid_auth import OpenIDKeystoneBackend
    django_openid_auth.OpenIDBackend = OpenIDKeystoneBackend

    from django_openid_auth import views as openid_views
    from tukey.openid_auth import login_begin as new_login_begin
    openid_views.login_begin = new_login_begin

    from tukey.openid_auth import login_complete as new_login_complete
    openid_views.login_complete = new_login_complete


    from openstack_dashboard.usage import base
    base.GlobalUsage.show_terminated = True

    from create_patches import patch
    patch()

