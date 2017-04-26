objects = ControllerManager()
deleted_objects = ControllerDeletionManager()

def __init__(self, *args, **kwargs):
    super(Controller, self).__init__(*args, **kwargs)
    self.no_sync=True

def __unicode__(self):  return u'%s %s %s' % (self.name, self.backend_type, self.version)

@property
def auth_url_v3(self):
    if self.auth_url and self.auth_url[-1] == '/':
        return '{}/v3/'.format('/'.join(self.auth_url.split('/')[:-2]))
    else:
        return '{}/v3/'.format('/'.join(self.auth_url.split('/')[:-1]))

@staticmethod
def select_by_user(user):

    if user.is_admin:
        qs = Controller.objects.all()
    else:
        from core.models.deploymentprivilege import DeploymentPrivilege
        deployments = [dp.deployment for dp in DeploymentPrivilege.objects.filter(user=user, role__role__in=['Admin', 'admin'])]
        qs = Controller.objects.filter(deployment__in=deployments)
    return qs
