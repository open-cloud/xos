
def handle(slice):
	from core.models import SiteDeployments,SliceDeployments,Deployment,Network,NetworkSlice,NetworkTemplate
	from collections import defaultdict
	site_deployments = SiteDeployments.objects.all()
	site_deploy_lookup = defaultdict(list)
	for site_deployment in site_deployments:
		site_deploy_lookup[site_deployment.site].append(site_deployment.deployment)
	
	slice_deployments = SliceDeployments.objects.all()
	slice_deploy_lookup = defaultdict(list)
	for slice_deployment in slice_deployments:
		slice_deploy_lookup[slice_deployment.slice].append(slice_deployment.deployment)
	
	all_deployments = Deployment.objects.all() 
	# slices are added to all deployments for now
	expected_deployments = all_deployments
	#expected_deployments = site_deploy_lookup[slice.site]
	for expected_deployment in expected_deployments:
		if slice not in slice_deploy_lookup or \
		   expected_deployment not in slice_deploy_lookup[slice]:
			sd = SliceDeployments(slice=slice, deployment=expected_deployment)
			sd.save()

	# make sure slice has at least 1 public and 1 private networkd
	public_net = None
	private_net = None
	networks = Network.objects.filter(owner=slice)
	for network in networks:
		if network.template.name == 'Public dedicated IPv4':
			public_net = network
		elif network.template.name == 'Private':
			private_net = network 
	if not public_net:
		public_net = Network(
          	name = slice.name+'-public',
          	template = NetworkTemplate.objects.get(name='Public dedicated IPv4'),
          	owner = slice
      		)
		public_net.save()
        
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
	net_slices = NetworkSlice.objects.filter(slice=slice, network__in=[public_net,private_net])
	for net_slice in net_slices:
		if net_slice.network == public_net:
			public_net_slice = net_slice 
		elif net_slice.network == private_net:
			private_net_slice = net_slice 
	if not public_net_slice:
		public_net_slice = NetworkSlice(slice=slice, network=public_net)
		public_net_slice.save()
	if not private_net_slice:
		private_net_slice = NetworkSlice(slice=slice, network=private_net)
		private_net_slice.save() 		
                      
             
        
	 
