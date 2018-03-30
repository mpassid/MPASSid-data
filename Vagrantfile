
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

   config.vm.box = "centos/7"
   # config.vm.box_url = "https://github.com/2creatives/vagrant-centos/releases/download/v6.4.2/centos64-x86_64-20140116.box"
   config.ssh.insert_key = false
   config.ssh.shell = 'bash --noprofile -l'

   config.vm.define "app" do |app|

       app.vm.network "private_network", ip: "192.168.0.150"
       app.vm.hostname = "mpass-app.local"
       app.vm.provision :ansible do |ansible|
           ansible.playbook = "ansible/mpass-data.yml"

       end

   end

   config.vm.synced_folder ".", "/vagrant", :mount_options => ["dmode=777", "fmode=666"]


end

