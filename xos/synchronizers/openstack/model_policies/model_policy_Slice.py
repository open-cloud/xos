from xos.config import Config

def handle_delete(slice):
    from core.models import Controller, ControllerSlice, SiteDeployment, Network, NetworkSlice,NetworkTemplate, Slice
    from collections import defaultdict

    public_nets = []
    private_net = None
    networks = Network.objects.filter(owner=slice)

    for n in networks:
        n.delete()	
    
    # Note that sliceprivileges and slicecontrollers are autodeleted, through the dependency graph

def handle(slice):
    from core.models import Controller, ControllerSlice, SiteDeployment, Network, NetworkSlice,NetworkTemplate, Slice
    from collections import defaultdict

    # only create nat_net if not using VTN
    support_nat_net = not getattr(Config(), "networking_use_vtn", False)

    print "MODEL POLICY: slice", slice

    # slice = Slice.get(slice_id)

    controller_slices = ControllerSlice.objects.filter(slice=slice)
    existing_controllers = [cs.controller for cs in controller_slices] 
        
    print "MODEL POLICY: slice existing_controllers=", existing_controllers

    all_controllers = Controller.objects.all()
    for controller in all_controllers:
        if controller not in existing_controllers:
            print "MODEL POLICY: slice adding controller", controller
            sd = ControllerSlice(slice=slice, controller=controller)
            sd.save()

    if slice.network in ["host", "bridged"]:
        # Host and Bridged docker containers need no networks and they will
        # only get in the way.
        print "MODEL POLICY: Skipping network creation"
    elif slice.network in ["noauto"]:
        # do nothing
        pass
    else:
        # make sure slice has at least 1 public and 1 private networkd
        public_nets = []
        private_nets = []
        networks = Network.objects.filter(owner=slice)
        for network in networks:
            if not network.autoconnect:
                continue
            if network.template.name == 'Public dedicated IPv4':
                public_nets.append(network)
            elif network.template.name == 'Public shared IPv4':
                public_nets.append(network)
            elif network.template.name == 'Private':
                private_nets.append(network)
        if support_nat_net and (not public_nets):
            # ensure there is at least one public network, and default it to dedicated
            nat_net = Network(
                    name = slice.name+'-nat',
                        template = NetworkTemplate.objects.get(name='Public shared IPv4'),
                    owner = slice
                    )
            if slice.exposed_ports:
                nat_net.ports = slice.exposed_ports
            nat_net.save()
            public_nets.append(nat_net)
            print "MODEL POLICY: slice", slice, "made nat-net"

        if not private_nets:
            private_net = Network(
                name = slice.name+'-private',
                template = NetworkTemplate.objects.get(name='Private'),
                owner = slice
            )
            private_net.save()
            print "MODEL POLICY: slice", slice, "made private net"
            private_nets = [private_net]
        # create slice networks
        public_net_slice = None
        private_net_slice = None
        net_slices = NetworkSlice.objects.filter(slice=slice, network__in=private_nets+public_nets)
        for net_slice in net_slices:
            if net_slice.network in public_nets:
                public_net_slice = net_slice
            elif net_slice.network in private_nets:
                private_net_slice = net_slice
        if support_nat_net and (not public_net_slice):
            public_net_slice = NetworkSlice(slice=slice, network=public_nets[0])
            public_net_slice.save()
            print "MODEL POLICY: slice", slice, "made public_net_slice"
        if not private_net_slice:
            private_net_slice = NetworkSlice(slice=slice, network=private_nets[0])
            private_net_slice.save()
            print "MODEL POLICY: slice", slice, "made private_net_slice"

    print "MODEL POLICY: slice", slice, "DONE"


