name             'nova-client-pdc'
maintainer       'HealthSeq'
maintainer_email 'satish@healthseq'
license          'All rights reserved'
description      'Installs/Configures nova-client'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          '0.3.3'
depends          'apt'


attribute 'cloud',
          :display_name => 'cloud',
          :description  => 'The clouds variables',
          :type         => 'array'

attribute 'nova',
          :display_name => 'nova',
          :description  => 'The nova variables',
          :type         => 'array'
