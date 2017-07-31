def tologdict(self):
    d=super(ControllerNetwork,self).tologdict()
    try:
        d['network_name']=self.network.name
        d['controller_name']=self.controller.name
    except:
        pass
    return d
