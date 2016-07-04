name 'logstash'
maintainer ''
maintainer_email ''
license 'WTFPL'
description 'Installs logstash'
version '1.1.4'
depends 'apt'

recipe 'logstash', 'Installs logstash forwarder'

%w(ubuntu debian).each do |os|
  supports os
end
