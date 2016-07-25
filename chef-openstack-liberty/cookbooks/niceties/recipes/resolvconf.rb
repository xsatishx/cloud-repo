# Changes by Satish
cookbook_file "/etc/resolvconf/resolv.conf.d/head" do
    mode "644"
    owner "root"
    group "root"
    source head
end