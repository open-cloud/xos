from planetstack.config import Config

try:
    observer_disabled = Config().observer_disabled
except:
    observer_disabled = False

print_once = True

if (not observer_disabled):
    from .event_manager import EventSender

    def notify_observer(model=None, delete=False):
        try:
            if (model and delete):
                EventSender().fire({'delete_flag':delete,'model':model.__name__}) 
            else:
                EventSender().fire()
        except Exception,e:
            print "Exception in Observer. This should not disrupt the front end. %s"%str(e)

else:
    def notify_observer(model=None, delete=False):
        if (print_once):
            print "The observer is disabled"
            print_once = False
        return
