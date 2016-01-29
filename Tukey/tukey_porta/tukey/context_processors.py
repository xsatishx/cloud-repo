from django.conf import settings # import the settings file

def logout_url(context):

    return {'LOGOUT_URL': settings.LOGOUT_URL}
