from xos.config import Config

try:
    observer_disabled = Config().observer_disabled
except:
    observer_disabled = False

def EnableObserver(x):
    """ used for manage.py --noobserver """
    global observer_disabled
    observer_disabled = not x

print_once = True

def notify_observer(model=None, delete=False, pk=None, model_dict={}):
    if (observer_disabled):
        global print_once
        if (print_once):
            print "The observer is disabled"
            print_once = False
        return

    try:
        from .event_manager import EventSender
        if (model and delete):
            if hasattr(model,"__name__"):
                modelName = model.__name__
            else:
                modelName = model.__class__.__name__
            EventSender().fire(delete_flag = delete, model = modelName, pk = pk, model_dict=model_dict)
        else:
            EventSender().fire()
    except Exception,e:
        print "Exception in Observer. This should not disrupt the front end. %s"%str(e)


