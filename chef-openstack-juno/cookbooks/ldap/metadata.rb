name             'ldap.conf'
maintainer       'HealthSeq'
maintainer_email 'satish@healthseq.com'
license          'All rights reserved'
description      'Installs/Configures keystone'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          '0.1.2'


attribute 'cloud',
          :display_name => 'cloud',
          :description  => 'The clouds FQDN',
          :type         => 'array'

attribute 'ldap',
          :display_name => 'ldap',
          :description  => 'ldap settings',
          :type         => 'array'
