def handle(controller_user):
    from core.models import ControllerUser, User
   
    try:
        my_status_code = int(controller_user.backend_status[0])
        try:
            his_status_code = int(controller_user.user.backend_status[0])
        except:
            his_status_code = 0
 
        if (my_status_code not in [0,his_status_code]):
            controller_user.user.backend_status = controller_user.backend_status
            controller_user.user.save(update_fields = ['backend_status'])
    except Exception,e:
        print str(e)	
        pass
