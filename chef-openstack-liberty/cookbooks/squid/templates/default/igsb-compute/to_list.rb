#!/usr/bin/env ruby
require 'json'

@usage = './to_list.rb <input file> <httpwhitelist> <httpwildcardwhitelist> <ftpwhitelist>'

unless ARGV.length == 4
  puts @usage
  exit
end

input_file_name = ARGV.first
@data = File.read(input_file_name).downcase
web_whitelist_filename=ARGV[1]
web_wildcard_whitelist_filename=ARGV[2]
ftp_whitelist_filename=ARGV[3]

def file_rx(rx)
  hash = {}
  @data.scan(rx) do |a, b|
    unless hash.include? a
      hash[a] = []
    end
    hash[a] += b.split
  end
  hash
end

def rough_count(hash)
  hash.each { |k, v| puts "#{k}:#{v.length}" }
end

dst_acl_rx = /^acl\s+(\S+)\s+dstdomain\s+([^\n#]+)/
port_acl_rx = /^acl\s+(\S+)\s+port\s+([^\n#]+)/
port_to_dst_rx = /^http_access allow\s+(\S+)\s+([^\n#]+)/

dst_acls = file_rx(dst_acl_rx)
port_acls = file_rx(port_acl_rx)
port_dst = file_rx(port_to_dst_rx)

[dst_acls, port_acls, port_dst].each do |h|
  rough_count(h)
  puts
end

port_dst.each { |k, v| puts k; puts v.join(', '); puts '======' }
puts
puts
puts 'Just looking for the ones in safe_ports in other places'
notsafeports = (port_dst.keys - ['safe_ports']).collect do |a|
  port_dst[a]
end.flatten.uniq

hostwhitelist = []
wildcardwhitelist = []
ftpwhitelist = []
acllist = []

port_dst['safe_ports'].each do |aclname|
  unless notsafeports.include? aclname
    acllist << aclname
  end
end

acllist.each do |acl|
  dst_acls[acl].each do |host|
    if host =~ /^\./
      wildcardwhitelist << host
    else
      hostwhitelist << host
    end
  end
end

port_dst['ftp_ports'].each do |i|
  dst_acls[i].each do |j|
    ftpwhitelist << j
  end
end

File.open(web_whitelist_filename,"w"){|f|f.puts hostwhitelist.sort}
File.open(web_wildcard_whitelist_filename,"w"){|f|f.puts wildcardwhitelist.sort}
File.open(ftp_whitelist_filename,"w"){|f|f.puts ftpwhitelist.sort}

puts wildcardwhitelist.to_json
