#Ml2 plugin config, layer 3 and dhcp
crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 type_drivers flat,vlan,vxlan
crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 tenant_network_types vxlan
#The Linux bridge agent only supports VXLAN overlay networks.
crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 mechanism_drivers linuxbridge,l2population
crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2 extension_drivers port_security
crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2_type_flat flat_networks public
crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini ml2_type_vxlan vni_ranges 1:1000
crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini securitygroup enable_ipset True
#Configure the Linux bridge agent
crudini --set /etc/neutron/plugins/ml2/linuxbridge_agent.ini linux_bridge physical_interface_mappings public:eth1
crudini --set /etc/neutron/plugins/ml2/linuxbridge_agent.ini vxlan enable_vxlan True
crudini --set /etc/neutron/plugins/ml2/linuxbridge_agent.ini vxlan local_ip 10.0.2.13
crudini --set /etc/neutron/plugins/ml2/linuxbridge_agent.ini vxlan l2_population True
crudini --set /etc/neutron/plugins/ml2/linuxbridge_agent.ini agent prevent_arp_spoofing True
crudini --set /etc/neutron/plugins/ml2/linuxbridge_agent.ini securitygroup enable_security_group True
crudini --set /etc/neutron/plugins/ml2/linuxbridge_agent.ini securitygroup firewall_driver neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
#Configure the layer-3 agent
crudini --set /etc/neutron/l3_agent.ini DEFAULT interface_driver neutron.agent.linux.interface.BridgeInterfaceDriver
crudini --set /etc/neutron/l3_agent.ini DEFAULT external_network_bridge 
crudini --set /etc/neutron/l3_agent.ini DEFAULT verbose True
#Configure the DHCP agent
crudini --set /etc/neutron/dhcp_agent.ini DEFAULT interface_driver neutron.agent.linux.interface.BridgeInterfaceDriver
crudini --set /etc/neutron/dhcp_agent.ini DEFAULT dhcp_driver neutron.agent.linux.dhcp.Dnsmasq
crudini --set /etc/neutron/dhcp_agent.ini DEFAULT enable_isolated_metadata True
crudini --set /etc/neutron/dhcp_agent.ini DEFAULT verbose True
crudini --set /etc/neutron/dhcp_agent.ini DEFAULT dnsmasq_config_file /etc/neutron/dnsmasq-neutron.conf
#Create and set DHCP
touch /etc/neutron/dnsmasq-neutron.conf
echo "dhcp-option-force=26,1450" >> /etc/neutron/dnsmasq-neutron.conf
#Config metadata
crudini --set /etc/neutron/metadata_agent.ini DEFAULT auth_uri http://dev-controller:5000
crudini --set /etc/neutron/metadata_agent.ini DEFAULT auth_url http://dev-controller:35357
crudini --set /etc/neutron/metadata_agent.ini DEFAULT auth_region RegionOne
crudini --set /etc/neutron/metadata_agent.ini DEFAULT auth_plugin password
crudini --set /etc/neutron/metadata_agent.ini DEFAULT project_domain_id default
crudini --set /etc/neutron/metadata_agent.ini DEFAULT user_domain_id default
crudini --set /etc/neutron/metadata_agent.ini DEFAULT project_name service
crudini --set /etc/neutron/metadata_agent.ini DEFAULT username neutron
crudini --set /etc/neutron/metadata_agent.ini DEFAULT password healthseq
crudini --set /etc/neutron/metadata_agent.ini DEFAULT nova_metadata_ip dev-controller
crudini --set /etc/neutron/metadata_agent.ini DEFAULT metadata_proxy_shared_secret healthseq
crudini --set /etc/neutron/metadata_agent.ini DEFAULT verbose True
#Configure compute to use the network
crudini --set /etc/nova/nova.conf neutron url http://dev-controller:9696
crudini --set /etc/nova/nova.conf neutron auth_url http://dev-controller:35357
crudini --set /etc/nova/nova.conf neutron auth_plugin password
crudini --set /etc/nova/nova.conf neutron project_domain_id default
crudini --set /etc/nova/nova.conf neutron user_domain_id default
crudini --set /etc/nova/nova.conf neutron region_name RegionOne
crudini --set /etc/nova/nova.conf neutron project_name service
crudini --set /etc/nova/nova.conf neutron username neutron
crudini --set /etc/nova/nova.conf neutron password healthseq
crudini --set /etc/nova/nova.conf neutron service_metadata_proxy True
crudini --set /etc/nova/nova.conf neutron metadata_proxy_shared_secret healthseq
#Finalize installation
