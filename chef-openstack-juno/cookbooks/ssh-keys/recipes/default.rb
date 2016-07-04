require 'openssl'

package 'pwgen' do
  action :install
end

#package 'ruby-shadow' do
#  action :install
#end

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
        comment "User created by chef"
        home ssh_user['dir']
        manage_home true
        notifies :unlock, "user[#{node_user}]"
        shell '/bin/bash'
      end

      # Preparing SSH keys
      ssh_keys = []

      Array(bag_users).each do |bag_user|
        data = data_bag_item('users', bag_user)
        if data and data['ssh_keys']
          ssh_keys += Array(data['ssh_keys'])
        end
      end

      # Saving SSH keys
      if ssh_keys.length > 0
        home_dir = ssh_user['dir']
        authorized_keys_file = "#{home_dir}/.ssh/authorized_keys"

        if node[:ssh_keys_keep_existing] && File.exist?(authorized_keys_file)
          Chef::Log.info("Keep authorized keys from: #{authorized_keys_file}")

          ## Loading existing keys
          #File.open(authorized_keys_file).each do |line|
          #  if line.start_with?("ssh")
          #    ssh_keys += Array(line.delete "\n")
          #  end
          #end

          ssh_keys.uniq!
        else
          # Creating ".ssh" directory
          directory "#{home_dir}/.ssh" do
            owner ssh_user['uid']
            group ssh_user['gid'] || user['uid']
            mode "0700"
          end
        end

        # Creating "authorized_keys"
        template authorized_keys_file do
          owner ssh_user['uid']
          group ssh_user['gid'] || user['uid']
          mode "0600"
          variables :ssh_keys => ssh_keys
        end
      end
    end
  end
end
