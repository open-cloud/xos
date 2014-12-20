from view_common import *

class DashboardWelcomeView(TemplateView):
    template_name = 'admin/dashboard/welcome.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context = getDashboardContext(request.user, context)
        return self.render_to_response(context=context)

class DashboardDynamicView(TemplateView):
    head_template = r"""{% extends "admin/dashboard/dashboard_base.html" %}
       {% load admin_static %}
       {% block content %}
    """

    head_wholePage_template = r"""{% extends "admin/wholePage.html" %}
       {% load admin_static %}
       {% block content %}
    """

    tail_template = r"{% endblock %}"

    def get(self, request, name="root", *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context = getDashboardContext(request.user, context)

        if name=="root":
            return self.multiDashboardView(request, context)
        elif kwargs.get("wholePage",None):
            return self.singleFullView(request, name, context)
        else:
            return self.singleDashboardView(request, name, context)

    def readTemplate(self, fn):
        TEMPLATE_DIRS = ["/opt/planetstack/templates/admin/dashboard/",
                         "/opt/planetstack/core/xoslib/dashboards/"]

        for template_dir in TEMPLATE_DIRS:
            pathname = os.path.join(template_dir, fn) + ".html"
            if os.path.exists(pathname):
                break
        else:
            return "failed to find %s in %s" % (fn, TEMPLATE_DIRS)

        template= open(pathname, "r").read()
        if (fn=="tenant"):
            # fix for tenant view - it writes html to a div called tabs-5
            template = '<div id="tabs-5"></div>' + template
        return template

    def embedDashboard(self, url):
        if url.startswith("template:"):
            fn = url[9:]
            return self.readTemplate(fn)
        elif url.startswith("http"):
            return '<iframe src="%s" width="100%%" height="100%%" style="min-height: 1024px;" frameBorder="0"></iframe>' % url
        else:
            return "don't know how to load dashboard %s" % url

    def multiDashboardView(self, request, context):
        head_template = self.head_template
        tail_template = self.tail_template

        body = """
         <div id="hometabs" >
         <ul id="suit_form_tabs" class="nav nav-tabs nav-tabs-suit" data-tab-prefix="suit-tab">
        """

        dashboards = request.user.get_dashboards()

        # customize is a special dashboard they always get
        customize = DashboardView.objects.filter(name="Customize")
        if customize:
            dashboards.append(customize[0])

        for i,view in enumerate(dashboards):
            body = body + '<li><a href="#dashtab-%d">%s</a></li>\n' % (i, view.name)

        body = body + "</ul>\n"

        for i,view in enumerate(dashboards):
            url = view.url
            body = body + '<div id="dashtab-%d">\n' % i
            if (view.controllers.all().count()>0):
                body = body + '<select id="dashselect-%d">' % i;
                for j,controllerdashboard in enumerate(view.controllerdashboards.all()):
                    body = body + '<option value="%d">%s</option>' % (j, controllerdashboard.controller.name)
                body = body + '</select>'

                for j,controllerdashboard in enumerate(view.controllerdashboards.all()):
                    body = body + '<div id="dashcontent-%d-%d" class="dashcontent-%d">\n' % (i,j,i)
                    body = body + self.embedDashboard(controllerdashboard.url);
                    body = body + '</div>\n';

                body = body + """<script>
                                 $("#dashselect-%d").change(function() { console.log("change!");
                                     v=$("#dashselect-%d").val();
                                     $(".dashcontent-%d").hide();
                                     $("#dashcontent-%d-" + v).show();
                                 });
                                 $(".dashcontent-%d").hide();
                                 $("#dashcontent-%d-0").show();
                                 </script>
                              """ % (i,i,i,i,i,i);
            else:
                body = body + self.embedDashboard(url)
            body = body + '</div>\n'

        body=body+"</div>\n"

        t = template.Template(head_template + body + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request = request,
            template = t,
            context = context,
            **response_kwargs)

    def singleDashboardView(self, request, name, context):
        head_template = self.head_template
        tail_template = self.tail_template

        t = template.Template(head_template + self.readTemplate(name) + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request = request,
            template = t,
            context = context,
            **response_kwargs)

    def singleFullView(self, request, name, context):
        head_template = self.head_wholePage_template
        tail_template = self.tail_template

        t = template.Template(head_template + self.readTemplate(name) + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request = request,
            template = t,
            context = context,
            **response_kwargs)

