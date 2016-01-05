def handle(controller_slice):
    from core.models import ControllerSlice, Slice
   
    try:
        my_status_code = int(controller_slice.backend_status[0])
        try:
            his_status_code = int(controller_slice.slice.backend_status[0])
        except:
            his_status_code = 0
 
        fields = []
        if (my_status_code not in [0,his_status_code]):
            controller_slice.slice.backend_status = controller_slice.backend_status
            fields+=['backend_status']

        if (controller_slice.backend_register != controller_slice.slice.backend_register):
            controller_slice.slice.backend_register = controller_slice.backend_register
            fields+=['backend_register']

        controller_slice.slice.save(update_fields = fields)

        
    except Exception,e:
        print str(e)	
        pass
