#views.py
from django.views.generic import TemplateView, View
import datetime

import json 
from core.models import Slice,SliceRole,SlicePrivilege,Site,Reservation
from django.http import HttpResponse


class DashboardWelcomeView(TemplateView):
    template_name = 'admin/dashboard/welcome.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        try:
            site = Site.objects.filter(id=request.user.site.id)
        except:
            site = Site.objects.filter(name="Princeton")
        context['site'] = site[0]

        context['userSliceInfo'] = getSliceInfo(request, context)
        context['cdnData'] = getCDNOperatorData();
        return self.render_to_response(context=context)

def getSliceInfo(request, context):
    sliceList = Slice.objects.all()
    slicePrivs = SlicePrivilege.objects.filter(user=request.user)
    userSliceInfo = []
    for entry in slicePrivs:

        try:
            reservationList = Reservation.objects.filter(slice=entry.slice)
            reservations = (True,reservationList)

        except:
            reservations = None

        userSliceInfo.append({'slice': Slice.objects.get(id=entry.slice.id),
                           'role': SliceRole.objects.get(id=entry.role.id).role,
                           'reservations': reservations})
    return userSliceInfo


def getCDNOperatorData(randomizeData = False):
    cdnData = {
        "Arizona": {
            "lat": 32.2333,
            "long": -110.94799999999998,
            "health": 0,
            "numNodes": 15,
            "numHPCSlivers": 2,
            "siteUrl": "http://www.cs.arizona.edu/"
        },
        "I2 Singapore": {
            "lat": 1.33544,
            "long": 103.88999999999999,
            "health": 0,
            "numNodes": 15,
            "numHPCSlivers": 5,
            "siteUrl": "http://www.internet2.edu/"
        },
        "ON.Lab": {
            "lat": 37.452955,
            "long": -122.18176599999998,
            "health": 0,
            "numNodes": 45,
            "numHPCSlivers": 12,
            "siteUrl": "http://www.onlab.us/"
        },
        "I2 Washington DC": {
            "lat": 38.009,
            "long": -77.00029999999998,
            "health": 0,
            "numNodes": 50,
            "numHPCSlivers": 7,
            "siteUrl": "http://www.internet2.edu/"
        },
        "I2 Seattle": {
            "lat": 47.6531,
            "long": -122.31299999999999,
            "health": 0,
            "numNodes": 100,
            "numHPCSlivers": 10,
            "siteUrl": "http://www.internet2.edu/"
        },
        "I2 Salt Lake City": {
            "lat": 40.7659,
            "long": -111.844,
            "health": 0,
            "numNodes": 35,
            "numHPCSlivers": 10,
            "siteUrl": "http://www.internet2.edu/"
        },
        "I2 New York": {
            "lat": 40.72,
            "long": -73.99000000000001,
            "health": 0,
            "numNodes": 25,
            "numHPCSlivers": 4,
            "siteUrl": "http://www.internet2.edu/"
        },
        "I2 Los Angeles": {
            "lat": 33.2505,
            "long": -117.50299999999999,
            "health": 0,
            "numNodes": 20,
            "numHPCSlivers": 10,
            "siteUrl": "http://www.internet2.edu/"
        },
        "I2 Kansas City": {
            "lat": 39.0012,
            "long": -94.00630000000001,
            "health": 0,
            "numNodes": 17,
            "numHPCSlivers": 8,
            "siteUrl": "http://www.internet2.edu/"
        },
        "I2 Houston": {
            "lat": 29.0077,
            "long": -95.00369999999998,
            "health": 0,
            "numNodes": 15,
            "numHPCSlivers": 10,
            "siteUrl": "http://www.internet2.edu/"
        },
        "I2 Chicago": {
            "lat": 41.0085,
            "long": -87.00650000000002,
            "health": 0,
            "numNodes": 15,
            "numHPCSlivers": 10,
            "siteUrl": "http://www.internet2.edu/"
        },
        "I2 Atlanta": {
            "lat": 33.0075,
            "long": -84.00380000000001,
            "health": 0,
            "numNodes": 15,
            "numHPCSlivers": 10,
            "siteUrl": "http://www.internet2.edu/"
        },
        "MaxPlanck": {
            "lat": 49.14,
            "long": 6.588999999999942,
            "health": 0,
            "numNodes": 15,
            "numHPCSlivers": 10,
            "siteUrl": "http://www.mpi-sws.mpg.de/"
        },
        "GeorgiaTech": {
            "lat": 33.7772,
            "long": -84.39760000000001,
            "health": 0,
            "numNodes": 15,
            "numHPCSlivers": 10,
            "siteUrl": "http://www.gatech.edu/"
        },
        "Princeton": {
            "lat": 40.3502,
            "long": -74.6524,
            "health": 0,
            "numNodes": 15,
            "numHPCSlivers": 10,
            "siteUrl": "http://princeton.edu/"
        },
        "Washington": {
            "lat": 47.6531,
            "long": -122.31299999999999,
            "health": 0,
            "numNodes": 15,
            "numHPCSlivers": 10,
            "siteUrl": "https://www.washington.edu/"
        },
        "Stanford": {
            "lat": 37.4294,
            "long": -122.17200000000003,
            "health": 0,
            "numNodes": 15,
            "numHPCSlivers": 10,
            "siteUrl": "http://www.stanford.edu/"
        },
    }

    if randomizeData:
        cdnData["Siobhan"] = { "lat": 43.34203, "long": -70.56351, "health": 10, "numNodes": 5, "numHPCSlivers": 3, "siteUrl": "https:devonrexes"}
        del cdnData["Princeton"]
        cdnData["I2 Seattle"]['siteUrl'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cdnData["I2 Salt Lake City"]["numHPCSlivers"] = 34


    return cdnData

class DashboardAjaxView(View):
    def get(self, request, **kwargs):
        return HttpResponse(json.dumps(getCDNOperatorData(True)), mimetype='application/javascript')
        
