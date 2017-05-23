class Meta:
    unique_together = ('image', 'controller')
         
objects = ControllerLinkManager()
deleted_objects = ControllerLinkDeletionManager()
