import os
from django.db import models
from django.forms.models import model_to_dict
from observer.event_manager import EventSender


class PlCoreBase(models.Model):

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True
		app_label = "core"

	def __init__(self, *args, **kwargs):
		super(PlCoreBase, self).__init__(*args, **kwargs)
		self.__initial = self._dict

	@property
	def diff(self):
		d1 = self.__initial
		d2 = self._dict
		diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
		return dict(diffs)

	@property
	def has_changed(self):
		return bool(self.diff)

	@property
	def changed_fields(self):
		return self.diff.keys()

	def get_field_diff(self, field_name):
		return self.diff.get(field_name, None)

	def delete(self, *args, **kwds):
		super(PlCoreBase, self).delete(*args, **kwds)

		EventSender().fire({'delete_flag':True,'model':self.__name__})

	def save(self, *args, **kwargs):
		super(PlCoreBase, self).save(*args, **kwargs)
		
		# Tell the observer that the source database has been updated
		EventSender().fire()

		self.__initial = self._dict

	@property
	def _dict(self):
		return model_to_dict(self, fields=[field.name for field in
							 self._meta.fields])



