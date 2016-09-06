from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django import template
from core.models import *
import json
import os
import time
import tempfile


class MCordView(TemplateView):
    head_template = r"""{% extends "admin/dashboard/dashboard_base.html" %}
       {% load admin_static %}
       {% block content %}
    """

    tail_template = r"{% endblock %}"

    def get(self, request, name="root", *args, **kwargs):
        head_template = self.head_template
        tail_template = self.tail_template

        title = request.GET.get('service', '')
        url = "/mcord/?service=%s" % (title)

        form = """
        <h2 class="content-title">Change %s Service</h2>
        <div id="content-main">
            <form class="form-horizontal">
                <div class="tab-content tab-content-main">
                    <div class="suit-include suit-tab suit-tab-administration hide">
                        <div class="left-nav">
                            <ul>
                                <li><a href="/admin/ceilometer/monitoringchannel/">Monitoring Channels</a></li>
                            </ul>
                        </div>
                    </div>
                    <fieldset class="module aligned suit-tab suit-tab-general show">
                        <div class="panel fieldset-body">
                            <div class="form-group field-backend_status_text ">
                                <label class="control-label col-xs-12 col-sm-2"><label>Backend status text:</label></label>
                                <div class="form-column col-xs-12 col-sm-8 col-md-6 col-lg-4">
                                    <p><img src="/static/admin/img/icon_clock.gif"> Pending sync, last_status = 0 - Provisioning in progress</p>
                                </div>
                            </div>
                            <div class="form-group field-name ">
                                <label class="control-label col-xs-12 col-sm-2"><label class="required" for="id_name">Name:</label></label>
                                <div class="form-column widget-AdminTextInputWidget col-xs-12 col-sm-8 col-md-6 col-lg-4">
                                    <input class="vTextField form-control" id="id_name" maxlength="30" name="name" type="text" value="%s">
                                    <div class="help-block">Service Name</div>
                                </div>
                            </div>
                            <div class="form-group field-enabled ">
                                <label class="control-label col-xs-12 col-sm-2"><label class="vCheckboxLabel" for="id_enabled">Enabled</label></label>
                                <div class="form-column widget-CheckboxInput col-xs-12 col-sm-8 col-md-6 col-lg-4">
                                    <input checked="checked" id="id_enabled" name="enabled" type="checkbox">
                                </div>
                            </div>
                            <div class="form-group field-versionNumber ">
                                <label class="control-label col-xs-12 col-sm-2"><label class="required" for="id_versionNumber">VersionNumber:</label></label>
                                <div class="form-column widget-AdminTextInputWidget col-xs-12 col-sm-8 col-md-6 col-lg-4">
                                    <input class="vTextField form-control" id="id_versionNumber" maxlength="30" name="versionNumber" type="text">
                                    <div class="help-block">Version of Service Definition</div>
                                </div>
                            </div>
                            <div class="form-group field-description ">
                                <label class="control-label col-xs-12 col-sm-2"><label for="id_description">Description:</label></label>
                                <div class="form-column widget-AdminTextareaWidget col-xs-12 col-sm-8 col-md-6 col-lg-4">
                                    <textarea class="vLargeTextField form-control" cols="40" id="id_description" maxlength="254" name="description" rows="10"></textarea>
                                    <div class="help-block">Description of Service</div>
                                </div>
                            </div>
                            <div class="form-group field-view_url ">
                                <label class="control-label col-xs-12 col-sm-2"><label for="id_view_url">View url:</label></label>
                                <div class="form-column widget-AdminTextInputWidget col-xs-12 col-sm-8 col-md-6 col-lg-4">
                                    <input class="vTextField form-control" id="id_view_url" maxlength="1024" name="view_url" type="text" value="%s">
                                </div>
                            </div>
                            <div class="form-group field-icon_url ">
                                <label class="control-label col-xs-12 col-sm-2"><label for="id_icon_url">Icon url:</label></label>
                                <div class="form-column widget-AdminTextInputWidget col-xs-12 col-sm-8 col-md-6 col-lg-4">
                                    <input class="vTextField form-control" id="id_icon_url" maxlength="1024" name="icon_url" type="text">
                                </div>
                            </div>
                        </div>
                    </fieldset>
                </div>
            </form>
            <div class="form-buttons clearfix">
                <button type="submit" class="btn btn-high btn-success" name="_save">Save</button>
                <button type="submit" name="_continue" class=" btn btn-high btn-info">Save and continue editing</button>
                <button type="submit" name="_addanother" class="btn btn-info">Save and add another</button>
                <a href="delete/" class="text-error deletelink">Delete</a>
            </div>
        </div>
        """ % (title, title, url)

        t = template.Template(head_template + form + tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=request,
            template=t,
            **response_kwargs
        )
