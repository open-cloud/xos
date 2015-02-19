def handle(controller_slice):
    from core.models import ControllerSlice, Slice
   
    try:
        my_status_code = int(controller_slice.backend_status[0])
        try:
            his_status_code = int(controller_slice.slice.backend_status[0])
        except:
            his_status_code = 0
 
        if (my_status_code not in [0,his_status_code]):
            controller_slice.slice.backend_status = controller_slice.backend_status
            controller_slice.slice.save(update_fields = ['backend_status'])
    except Exception,e:
        print str(e)	
        pass
