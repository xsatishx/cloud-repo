name              "collectd"
maintainer        ""
maintainer_email  ""
license           "WTFPL"
description       "Installs collectd"
version           "1.1.4"

recipe "collectd", "Installs collectd"

%w{ ubuntu debian }.each do |os|
  supports os
end
