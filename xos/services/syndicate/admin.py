from core.admin import ReadOnlyAwareAdmin, SliceInline
from core.middleware import get_request
from core.models import User

from django import forms
from django.contrib import admin

from services.syndicate.models import *


class SyndicateServiceForm(forms.ModelForm):

    class Meta:
        model = SyndicateService


class VolumeForm(forms.ModelForm):

    class Meta:
        model = Volume

