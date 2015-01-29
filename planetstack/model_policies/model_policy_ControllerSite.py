def handle(controller_site):
    from core.models import ControllerSite, Site
   
    try:
        my_status_code = int(controller_site.backend_status[0])
        try:
            his_status_code = int(controller_site.site.backend_status[0])
        except:
            his_status_code = 0
 
        if (my_status_code not in [0,his_status_code]):
            controller_site.site.backend_status = controller_site.backend_status
            controller_site.site.save(update_fields = ['backend_status'])
    except Exception,e:
        print str(e)	
        pass
