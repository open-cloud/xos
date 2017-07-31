def tologdict(self):
    d=super(ControllerSlice,self).tologdict()
    try:
        d['slice_name']=self.slice.name
        d['controller_name']=self.controller.name
    except:
        pass
    return d
