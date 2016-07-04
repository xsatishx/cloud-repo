name             'nova-keystone-pdc'
maintainer       'HealthSeq'
maintainer_email 'satish@healthseq.com'
license          'All rights reserved'
description      'Installs/Configures keystone'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          '0.3.3'

attribute 'cloud',
          :display_name => 'cloud',
          :description  => 'The clouds variables',
          :type         => 'array'

attribute 'keystone',
          :display_name => 'keystone',
          :description  => 'The keystoen variables',
          :type         => 'array'

attribute 'rabbitmq',
          :display_name => 'rabbitmq',
          :description  => 'The rabbitmqvariables',
          :type         => 'array'

attribute 'ssl',
          :display_name => 'ssl',
          :description  => 'ssl certificates',
          :type         => 'array'

