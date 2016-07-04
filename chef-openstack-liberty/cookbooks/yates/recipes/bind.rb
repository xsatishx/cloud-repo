#
# Cookbook Name:: yates
# Recipe:: bind
#
# This doesn't actually configure or install bind.
# This just creates zone files to be dropped into place.

dropoff="/usr/local/generatedzoness"

pxe_hosts = data_bag_item("yates", "pxe_hosts_old")
hosts = pxe_hosts['hosts']
clouds = pxe_hosts['clouds']

#nodes = data_bag_item("yates", "pxe_hosts")
nodes = data_bag_item("yates", "nodes")
#No longer trust any other dbags.

racks = Hash.new() {|h,k|h[k]={}}
nodes.each do |hostname,data|
  next unless data.include?"rack"
  rack=data["rack"]
  ip=data["ip"]
  racks[rack][hostname]=ip
end

racks.each do |rack,hosts|
  template "#{dropoff}/#{rack}.zone" do
    mode "644"
    owner "root"
    group "root"
    source "bind/zone.erb"
    action :create
    variables(:hosts=>hosts)
  end
end
