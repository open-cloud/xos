#views.py
from django.views.generic import TemplateView

from core.models import Slice,SliceRole,SlicePrivilege,Site,Reservation

class DashboardWelcomeView(TemplateView):
    template_name = 'admin/dashboard/welcome.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        sliceList = Slice.objects.all()
        try:
            site = Site.objects.filter(id=request.user.site.id)
        except:
            site = Site.objects.filter(name="Princeton")
        context['site'] = site[0]

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

        context['userSliceInfo'] = userSliceInfo
        return self.render_to_response(context=context)
