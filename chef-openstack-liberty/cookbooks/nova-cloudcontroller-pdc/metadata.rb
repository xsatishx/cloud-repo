name             'nova-cloudcontroller-pdc'
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

attribute 'keystone',
          :display_name => 'keystone',
          :description  => 'The keystoen variables',
          :type         => 'array'

attribute 'mysql',
          :display_name => 'mysql',
          :description  => 'mysql settings',
          :type         => 'array'

attribute 'rabbitmq',
          :display_name => 'rabbitmq',
          :description  => 'The rabbitmqvariables',
          :type         => 'array'

attribute 'nova',
          :display_name => 'nova',
          :description  => 'The nova variables',
          :type         => 'array'
