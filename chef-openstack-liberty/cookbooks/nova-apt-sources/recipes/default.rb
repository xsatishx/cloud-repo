runonce=false

cloudtoversion={"pdcv3"=>"juno"}

if cloudtoversion.include?node.cloud.chef_version
  #Yes, you have to make a new entry in the cloudtoversion mapping for each cloud
  #and populate the files directory with directories named after the openstack release
  #and sources.list files named for each ubuntu release we're dealing with
  version=cloudtoversion[node.cloud.chef_version]
  codename=node.lsb.codename

  cookbook_file "/etc/apt/sources.list.d/ubuntu-cloud-archive-#{version}-#{codename}.list" do
    source "#{version}/ubuntu-cloud-archive-#{version}-#{codename}.list"
    mode "0644"
    owner "root"
    group "root"
    runonce=true
  end

  package "ubuntu-cloud-keyring" do
    action :install
    action :upgrade
  end

  if runonce
    %x{apt-get update}
  end
end
