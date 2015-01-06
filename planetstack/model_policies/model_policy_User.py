def handle(user):
    from core.models import Controller, ControllerSite, ControllerUser
    from collections import defaultdict
    
    controller_users = ControllerUser.objects.filter(user=user)
    existing_controllers = [cu.controller for cu in controller_users]
    all_controllers = Controller.objects.all()
    for controller in all_controllers:
        if controller not in existing_controllers:
            ctrl_user = ControllerUser(controller=controller, user=user)
            ctrl_user.save()  

