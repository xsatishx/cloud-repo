name             'cpu'
maintainer       'healthseq'
maintainer_email 'satish@healthseq.com'
license          'All rights reserved'
description      'Installs/Configures keystone'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          '0.3.0'


attribute 'cloud',
          :display_name => 'cloud',
          :description  => 'The clouds variables',
          :type         => 'array'

attribute 'ldap',
          :display_name => 'ldap',
          :description  => 'The ldap variables',
          :type         => 'array'

attribute 'cpu',
          :display_name => 'cpu',
          :description  => 'The cpu variables',
          :type         => 'array'
