def handle(slice_privilege):
    from core.models import Controller, SlicePrivilege, ControllerSlicePrivilege
   
    # slice_privilege = SlicePrivilege.get(slice_privilege_id) 
    # apply slice privilage at all controllers
    controller_slice_privileges = ControllerSlicePrivilege.objects.filter(
        slice_privilege = slice_privilege,
        )
    existing_controllers = [sp.controller for sp in controller_slice_privileges]
    all_controllers = Controller.objects.all()
    for controller in all_controllers:
        if controller not in existing_controllers:
            ctrl_slice_priv = ControllerSlicePrivilege(controller=controller, slice_privilege=slice_privilege)
            ctrl_slice_priv.save()  

