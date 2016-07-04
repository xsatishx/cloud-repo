name             'ceph'
maintainer       'Laboratory for Advanced Computing'
maintainer_email 'rpowell1@uchicago.edu'
license          'All rights reserved'
description      'Installs/Configures keystone'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          '0.3.0'
depends          'apt'


attribute 'cloud',
          :display_name => 'cloud',
          :description  => 'The clouds variables',
          :type         => 'array'

attribute 'ceph',
          :display_name => 'ceph',
          :description  => 'The ceph variables',
          :type         => 'array'
