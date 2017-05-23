objects = ControllerLinkManager()
deleted_objects = ControllerLinkDeletionManager()

class Meta:
    unique_together = ('site', 'deployment', 'controller')

