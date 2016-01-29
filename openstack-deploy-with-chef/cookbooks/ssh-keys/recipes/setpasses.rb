require 'openssl'

package 'pwgen' do
  action :install
end

package 'ruby-shadow' do
  action :install
end

if node[:ssh_keys]
  node[:ssh_keys].each do |node_user, bag_users|
    next unless node_user
    next unless bag_users

    # Getting node user data
    ssh_user = node['etc']['passwd'][node_user]

    # Defaults for new user
    ssh_user = {'uid' => node_user, 'gid' => node_user, 'dir' => "/home/#{node_user}"} unless ssh_user

    if ssh_user and ssh_user['dir'] and ssh_user['dir'] != "/dev/null"
      #Create user if necessary
      user node_user do
        home ssh_user['dir']
        manage_home true
        notifies :unlock, "user[#{node_user}]"
        shell '/bin/bash'
        password lazy{%x{openssl passwd -1 $(pwgen -s 64 1)}.strip}
      end
    end
  end
end
