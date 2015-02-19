# Implement this interface
# to serve as a driver for analytics

class DashboardStatistics(dict):
    def __init__(self):
        self['stat_list'] = []
        self['average'] = 0
        self['sum'] = 0
        self['unit'] = 'units'
        self['stat_list']=[]
        # stat_list is a list of dicts
        # [ {'timestamp': datetime, 'value': value} ]


class MonitorDriver:
    def __init__(self):
        pass

    def get_meter(self, meter_name, obj, pk, credentials=None):
        pass
