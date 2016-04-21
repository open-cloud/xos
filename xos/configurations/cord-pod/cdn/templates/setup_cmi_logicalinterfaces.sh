lab="External"
for service in ["HyperCache", "RequestRouter"]:
    for node in ListAll("Node"):
        node_id = node["node_id"]
        for interface_id in node["interface_ids"]:
            iface=Read("Interface", interface_id)
            if iface["is_primary"] and len(iface["ip_address_ids"])==1:
                ip_id = iface["ip_address_ids"][0]
                if ListAll("LogicalInterface", {"node_id": node_id, "ip_address_ids": [ip_id], "label": lab, "service": service}):
                    print "External label exists for node", node_id, "ip", ip_id, "service", service
                else:
                    print "Adding external label for node", node_id, "ip", ip_id, "service", service
                    li = Create("LogicalInterface", {"node_id": node_id, "label": lab, "service": service})
	            Bind("LogicalInterface", li, "IpAddress", ip_id)
