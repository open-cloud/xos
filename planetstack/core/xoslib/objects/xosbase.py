import datetime
import time

class XOSBase(object):
    name = "XOSBase"

    def __init__(self):
        pass

    def ensure_serializable(self, d):
        d2={}
        for (k,v) in d.items():
            # datetime is not json serializable
            if isinstance(v, datetime.datetime):
                d2[k] = time.mktime(v.timetuple())
            elif v.__class__.__name__ == "Geoposition":
                pass
            else:
                d2[k] = v
        return d2

