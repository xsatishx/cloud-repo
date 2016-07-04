apt_repository 'logstashforwarder' do
  # deb http://packages.elasticsearch.org/logstashforwarder/debian stable main
  components ['main']
  distribution 'stable'
  uri 'https://packages.elastic.co/beats/apt'
#  keyserver 'packages.elasticsearch.org:80'
  key 'https://packages.elasticsearch.org/GPG-KEY-elasticsearch'
#  key 'GPG-KEY-elasticsearch'
  action :add
end

directory '/etc/pki/tls/certs/' do
  action :create
  recursive true
  mode '0755'
  owner 'root'
  group 'root'
end


directory '/etc/filebeat/' do
  action :create
  recursive true
  mode '0755'
  owner 'root'
  group 'root'
end

cookbook_file '/etc/pki/tls/certs/logstash-forwarder.crt' do
  source 'logstash-forwarder.crt'
  mode '0644'
  owner 'root'
  group 'root'
end

package 'logstash-forwarder' do
  action :install
end

cookbook_file '/etc/filebeat/filebeat.yaml' do
  source 'filebeat.yaml'
  mode '0644'
  owner 'root'
  group 'root'
  #  notifies :restart, "service[filebeat]"
end
