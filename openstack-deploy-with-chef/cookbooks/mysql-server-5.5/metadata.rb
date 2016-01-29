name             'mysql-server-5.5'
maintainer       'HealthSeq'
maintainer_email 'satish@healthseq.com'
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


