## Set up a new CDN

### CDN on VTN - headnode

1. nova flavor-create --is-public true m1.cdnnode auto 8192 110 4
2. in XOS create flavor m1.cdnnode and add to deployment

### CDN on VTN - CMI

1. Make sure plenty of glance space on ctl node
2. Make sure plenty of instance space on compute nodes
3. Install cmi-0.3.img into XOS images/ directory
4. Install CentOS-6-cdnnode-0.3.img into XOS images/ directory
5. Wait for these two images to be loaded into glance (check glance image-list for status)
6. XOS UI: Add cmi and CentOS images to MyDeployment
7. Run recipe xos/configurations/cord-pod/pod-cdn.yaml
       * this will create mysite_cdn slice, cdn-public network, and add management and cdn-public networks to slice
8. Instantiate CMI instance in mysite_cdn
       * flavor: m1.large
       * image: cmi-0.3.img
9. edit configurations/cord-pod/cdn/cmi-settings.sh
       * update COMPUTE_NODE and MGMT_IP to match CMI instance
       * update NODE_KEY to match ssh key for root @ the compute node
       * do not change VM_KEY; the pubkey is baked into the instance
10. edit configurations/cord-pod/cdn/cmi.yaml
       * update gateway_ip and gateway_mac to reflect public internet gateway CMI will use
11. copy the keygen and allkeys.template to the private/ directory
12. copy cmi_id_rsa
13. run setup-cmi.sh
       * this will SSH into the CMI and run setup, then modify some settings.
       * it may take a long time, 10-20 minutes or more
       * takeover script will be saved to takeovers/. Takeover script will be used in the next phase.

### CDN on VTN - cdnnode

1. Instantiate cdnnode instance in mysite_cdn
       * flavor: m1.cdnnode
       * CenOS-6-cdnnode-0.3.img
2. Log into compute node and Attach disk
       * virsh attach-disk <instance_name> /dev/sdc vdc --cache none
       * (make sure this disk wasn't used anywhere else!)
3. log into cdnnode VM
       * make sure default gateway is good (check public connectivity)
       * make sure arp table is good
       * make sure CMI is reachable from cdnnode
       * run takeover script that was created by the CMI 
       * (I suggest commenting out the final reboot -f, and make sure the rest of it worked right before rebooting)
       * Node will take a long time to install
4. log into cdnnode
       * to SSH into cdnnode, go into CMI, vserver coplc, cd /etc/planetlab, and use debug_ssh_key.rsa w/ root user
       * check default gateway
       * fix arp entry for default gateway

### CDN on VTN - cmi part 2

1. run setup-logicalinterfaces.sh

### CDN on VTN - important notes

We manually edited synchronizers/vcpe/templates/dnsasq_safe_servers.j2 inside the vcpe synchronizer VM:

    # temporary for ONS demo
    address=/z.cdn.turner.com/207.141.192.134
    address=/cnn-vh.akamaihd.net/207.141.192.134

### Test Commands

* First, make sure the vSG is the only DNS server available in the test client. 
* Second, make sure cdn_enable bit is set in CordSubscriber object for your vSG.
* curl -L -vvvv http://downloads.onosproject.org/vm/onos-tutorial-1.1.0r220-ovf.zip > /dev/null
* curl -L -vvvv http://onlab.vicci.org/onos-videos/Nov-planning-day1/Day1+00+Bill+-+Community+Growth.mp4 > /dev/null
* curl -L -vvvv http://downloads.onosproject.org/release/onos-1.2.0.zip > /dev/null

## Restart CDN after power-down

To do...
test
