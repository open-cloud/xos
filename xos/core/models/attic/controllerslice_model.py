class Meta:
    unique_together = ('controller', 'slice')
 
def tologdict(self):
    d=super(ControllerSlice,self).tologdict()
    try:
        d['slice_name']=self.slice.name
        d['controller_name']=self.controller.name
    except:
        pass
    return d

@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = ControllerSlice.objects.all()
    else:
        slices = Slice.select_by_user(user)
        qs = ControllerSlice.objects.filter(slice__in=slices)
    return qs    

