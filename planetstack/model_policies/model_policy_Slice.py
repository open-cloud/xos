
def handle(slice):
	from core.models import Controller, ControllerSiteDeployments, ControllerSlices,Controller,Network,NetworkSlice,NetworkTemplate
	from collections import defaultdict
	ctrl_site_deployments = ControllerSiteDeployments.objects.all()
	site_deploy_lookup = defaultdict(list)
	for ctrl_site_deployment in ctrl_site_deployments:
		site_deploy_lookup[ctrl_site_deployment.site_deployment].append(ctrl_site_deployment)
	
	slice_controllers = ControllerSlices.objects.all()
	slice_deploy_lookup = defaultdict(list)
	for slice_controller in slice_controllers:
		slice_deploy_lookup[slice_controller.slice].append(slice_controller)
	
	#expected_controllers = site_deploy_lookup[slice.site]
        all_controllers = Controller.objects.all() 
	for expected_controller in controllers:
		if slice not in slice_deploy_lookup or \
		   expected_controller not in slice_deploy_lookup[slice]:
			sd = ControllerSlices(slice=slice, controller=expected_controller)
			sd.save()

	# make sure slice has at least 1 public and 1 private networkd
	public_nets = []
	private_net = None
	networks = Network.objects.filter(owner=slice)
	for network in networks:
		if network.template.name == 'Public dedicated IPv4':
			public_nets.append(network)
		elif network.template.name == 'Public shared IPv4':
			public_nets.append(network)
		elif network.template.name == 'Private':
			private_net = network
	if not public_nets:
                # ensure there is at least one public network, and default it to dedicated
		nat_net = Network(
          	    name = slice.name+'-nat',
             	    template = NetworkTemplate.objects.get(name='Public shared IPv4'),
          	    owner = slice
      		    )
		nat_net.save()
                public_nets.append(nat_net)

	if not private_net:
        	private_net = Network(
          	name = slice.name+'-private',
          	template = NetworkTemplate.objects.get(name='Private'),
          	owner = slice
      		)
      		private_net.save()
	# create slice networks
	public_net_slice = None
	private_net_slice = None
	net_slices = NetworkSlice.objects.filter(slice=slice, network__in=[private_net]+public_nets)
	for net_slice in net_slices:
		if net_slice.network in public_nets:
			public_net_slice = net_slice
		elif net_slice.network == private_net:
			private_net_slice = net_slice
	if not public_net_slice:
		public_net_slice = NetworkSlice(slice=slice, network=public_nets[0])
		public_net_slice.save()
	if not private_net_slice:
		private_net_slice = NetworkSlice(slice=slice, network=private_net)
		private_net_slice.save()




