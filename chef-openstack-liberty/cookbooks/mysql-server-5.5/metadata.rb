name             'mysql-server-5.5'
maintainer       'Laboratory for Advanced Computing'
maintainer_email 'rpowell1@uchicago.edu'
license          'All rights reserved'
description      'mysql'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          '0.1.2'


attribute 'cloud',
          :display_name => 'cloud',
          :description  => 'The clouds FQDN',
          :type         => 'array'

attribute 'mysql',
          :display_name => 'mysql',
          :description  => 'mysql settings',
          :type         => 'array'


