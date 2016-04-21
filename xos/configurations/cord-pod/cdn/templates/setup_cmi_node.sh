site_id=GetSites()[0]["site_id"]
nodeinfo = {'hostname': "{{ node_hostname }}", 'dns': "8.8.8.8"}
n_id = AddNode(site_id, nodeinfo)
mac = "DE:AD:BE:EF:00:01"
interfacetemplate = {'mac': mac, 'kind': 'physical', 'method': 'static', 'is_primary': True, 'if_name': 'eth0'}
i_id = AddInterface(n_id, interfacetemplate)
ip_addr = "169.254.169.1" # TO DO: get this from Neutron in the future
netmask = "255.255.255.254" # TO DO: get this from Neutron in the future
ipinfo = {'ip_addr': ip_addr, 'netmask': netmask, 'type': 'ipv4'}
ip_id = AddIpAddress(i_id, ipinfo)
routeinfo = {'interface_id': i_id, 'next_hop': "127.0.0.127", 'subnet': '0.0.0.0', 'metric': 1}
r_id = AddRoute(n_id, routeinfo)
hpc_slice_id = GetSlices({"name": "co_coblitz"})[0]["slice_id"]
AddSliceToNodes(hpc_slice_id, [n_id])
dnsdemux_slice_id = GetSlices({"name": "co_dnsdemux"})[0]["slice_id"]
dnsredir_slice_id = GetSlices({"name": "co_dnsredir_coblitz"})[0]["slice_id"]
AddSliceToNodes(dnsdemux_slice_id, [n_id])
AddSliceToNodes(dnsredir_slice_id, [n_id])
takeoverscript=GetBootMedium(n_id, "node-cloudinit", '')
file("/root/takeover-{{ node_hostname }}","w").write(takeoverscript)
