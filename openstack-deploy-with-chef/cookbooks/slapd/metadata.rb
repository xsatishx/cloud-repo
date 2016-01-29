name             'slapd'
maintainer       'HealthSeq'
maintainer_email 'satish@healthseq.com'
license          'All rights reserved'
description      'Installs/Configures keystone'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          '0.3.3'


attribute 'cloud',
          :display_name => 'cloud',
          :description  => 'The clouds FQDN',
          :type         => 'array'

attribute 'ldap',
          :display_name => 'ldap',
          :description  => 'ldap settings',
          :type         => 'array'

attribute 'ssl',
          :display_name => 'ssl',
          :description  => 'ssl keys',
          :type         => 'array'
