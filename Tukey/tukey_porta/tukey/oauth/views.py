from django.shortcuts import render,redirect
from oauth_backend import OauthBackend
from django.http import HttpResponse, HttpResponseForbidden
from django.http import Http404
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib.auth import authenticate, login
from tukey.models import UnregisteredUser
import urllib,json,requests
from openstack_auth.exceptions import KeystoneAuthException
backend=OauthBackend()



def index(request):
    '''
    Login entry for google oauth2.0, an antiforgery token is created 
    and user is redirected to google oauth endpoint
    '''
    state=get_random_string(length=32)
    parameters=settings.OAUTH['parameters'].copy()
    parameters['state']=state
    request.session['oauth_state']=state
    request.session['next']=request.GET.get('next','/project')
    return redirect(settings.OAUTH['auth_uri']+"?"+\
        urllib.urlencode(parameters))


def oauth2callback(request):
    '''
    Endpoint for google  oauth2.0 callback, the antiforgery token is checked,
    then tukey talk to google using the code in the request, and exchange user
    information from google, user email is extracted from id_token
    '''
    if request.session.get('oauth_state','')==request.GET['state']:
        token=backend.getToken(request.GET.get('code',''))
        if token.has_key('id_token'):
            email=backend.decode(token['id_token'])
        else:
            return render(request,'403.html',{},status=403)
        try:
            user=authenticate(password=settings.TUKEY_PASSWORD,username='openid %s' % email,\
                auth_url=settings.OPENSTACK_KEYSTONE_URL,request=request)
            user.identifier=email
            if user!=None and user.is_active:
                login(request,user)
                return redirect(request.session.get('next','/project'))
        
        #create unregistered user if user is not authorized in keystone,
        #and redirect user to apply page
        except KeystoneAuthException:
            user=UnregisteredUser('OpenId',email)
            from tukey.webforms.views import osdc_apply
            return osdc_apply(request, user)

    else:
        return render(request,'403.html',{},status=403)


