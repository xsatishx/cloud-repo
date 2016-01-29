============
Tukey Portal
============

Tukey Portal is built over Django leveraging Horizon for OpenStack and
Eucalyptus VM management.

Installation
============
You can install by modifying and running install.sh as a user that has
passwordless sudo

Before you run install.sh modify the user settings in the section starting with
# USER SETTINGS ----- 

Horizon Info
============

Horizon is a Django-based project that provides a complete OpenStack
Dashboard along with an extensible framework for building new dashboards
from reusable components. The ``openstack_dashboard`` module is a reference
implementation of a Django site that uses the ``horizon`` app to provide
web-based interactions with the various OpenStack projects.

For release management:

 * https://launchpad.net/horizon

For blueprints and feature specifications:

 * https://blueprints.launchpad.net/horizon

For issue tracking:

 * https://bugs.launchpad.net/horizon

Dependencies
============

Install tukey-middleware https://github.com/opencloudconsortium/tukey-middleware
Horizon and other dependencies will be install by the install.sh script and can
be found there.


Running with Apache
===================

ln -s PATH_TO_TUKEY_PORTAL/openstack-dashboard.conf  /etc/apache2/conf.d/openstack-dashboard.conf


