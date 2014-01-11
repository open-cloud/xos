#views.py
from django.views.generic import TemplateView


class DashboardWelcomeView(TemplateView):
    template_name = 'admin/dashboard/welcome.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context=context)
