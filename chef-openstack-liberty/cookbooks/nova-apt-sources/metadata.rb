name              "nova-apt-sources"
maintainer        ""
maintainer_email  ""
license           "WTFPL"
description       "Installs nova sources.list"
version           "0.0.1"

%w{ ubuntu debian }.each do |os|
  supports os
end
