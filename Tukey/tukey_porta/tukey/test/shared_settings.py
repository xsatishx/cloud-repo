
# For times when a user needs to choose a resource to perform a
# certain action on we need to know what resources support that
# function those functions are currently:
CLOUD_FUNCTIONS = {
    'import_keypair': ['sullivan', 'loginadler', 'loginsullivan', 'all'],
    'create_keypair': ['adler', 'sullivan', 'loginadler', 'loginsullivan', 'all'],
    'associate_ip': ['sullivan'],
    'edit_instance': ['sullivan'],
    'launch_multiple': ['sullivan'],
    'namable_servers': ['sullivan']
}

# Cloud ids that will match the tukey-middleware etc/enabled config
# files as keys and the values a short description
CLOUD_DETAILS = {
    'loginadler': 'Adler login server',
    'loginsullivan': 'Sullivan login server',
    'adler':    'Adler instances',
    'sullivan': 'Sullivan instances',
    'all': 'All Resources'
#     'sc12':   'SC12 Demo Cloud'
}

AUTH_MEMCACHED = '127.0.0.1:11211'

# Shibboleth headers we want to consume in the order we want to
# check for them
SHIB_HEADERS = ('HTTP_EPPN',)

USAGE_ATTRIBUTES = {
    'OCC-Y Hadoop Disk (GB):': "occ_y_hdfsdu",
    'OCC-Y Jobs:': "occ_y_jobs",
    'Adler Glusterfs Disk (GB):': "adler_du",
    'Sullivan Glusterfs Disk (GB):': "sullivan_du",
    'Sullivan Cloud Virtual Cores:': "sullivan_cores",
    'Sullivan Cloud RAM Hours (GB Hours):': "sullivan_ram",
    'Adler Cloud RAM Hours (GB Hours):': "adler_ram",
    'Adler Cloud Virtual Cores:': "adler_cores",
    'OCC LVOC Hadoop Disk (GB):': "occ_lvoc_hdfsdu",
    'OCC LVOC Jobs:': "occ_lvoc_jobs"}


AUTHENTICATION_BACKENDS = (
     'django_openid_auth.auth.OpenIDBackend',
     'openstack_auth.backend.KeystoneBackend',
)

DISABLE_SECURITY_GROUPS_AND_IPS = True
