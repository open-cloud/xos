def controller_setter(instance, **kwargs):
    try:
        instance.controller = instance.node.site_deployment.controller
    except:
        instance.controller = None

models.signals.post_init.connect(controller_setter, Instance)
