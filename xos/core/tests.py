#!/usr/bin/env python
from django.test import TestCase
from core.models import *
from rest_framework.test import *
from genapi import *
import json
from datetime import datetime

FIXTURES_FILE = 'core/fixtures/initial_data.json'
MODELS = ['Deployment','Image','Node','Reservation','Slice','Instance','User']

def is_dynamic_type(x):
	t = type(x)
	return t in [datetime]

class APITestCase(TestCase):
	def setUp(self):
		self.init_data=json.loads(open(FIXTURES_FILE).read())
		self.data_dict={}
		self.hidden_keys={}

		for d in self.init_data:
			model_tag = d['model']
			model_name = model_tag.split('.')[1]

			try:
				self.data_dict[model_name].append(d)
			except:
				self.data_dict[model_name]=[d]

		# Any admin user would do
		self.calling_user = User('sapan@onlab.us')
		self.client = APIClient()
		self.client.force_authenticate(user=self.calling_user)


	def check_items(self, response, data_list):
		rdict = {}
		for r in response:
			rdict['%d'%r['id']]=r

		for d in data_list:
			match = True
			try:
				item = rdict['%d'%d['pk']]
			except Exception,e:
				print 'API missing item %d / %r'%(d['pk'],rdict.keys())
				raise e

			fields=d['fields']
			fields['id']=d['pk']

			for k in item.keys():
				try:
					resp_val = fields[k]
				except KeyError:
					if (not self.hidden_keys.has_key(k)):
						print 'Hidden key %s'%k
						self.hidden_keys[k]=True

					continue

				if (item[k]!=resp_val and not is_dynamic_type(item[k])):
					if (type(resp_val)==type(item[k])):
						print 'Key %s did not match: 1. %r 2. %r'%(k,item[k],resp_val)
						print fields
						match = False



	def create(self, model, mplural, record):
		request = self.client.put('/xos/%s/'%mplural,record['fields'])

		#if (len2==len1):
		#	raise Exception('Could not delete %s/%d'%(model,pk))

		return

	def update(self, model, mplural, pk):
		src_record = self.data_dict[model.lower()][0]
		record_to_update = src_record['fields']
		now = datetime.now()
		record_to_update['enacted']=now
		response = self.client.put('/xos/%s/%d/'%(mplural,pk),record_to_update)
		self.assertEqual(response.data['enacted'],now)

		return

	def delete(self, model, mplural, pk):
		mclass = globals()[model]
		len1 = len(mclass.objects.all())
		response = self.client.delete('/xos/%s/%d/'%(mplural,pk))
		len2 = len(mclass.objects.all())
		self.assertNotEqual(len1,len2)

		return

	def retrieve(self, m, mplural, mlower):
		response = self.client.get('/xos/%s/'%mplural)
		#force_authenticate(request,user=self.calling_user)
		self.check_items(response.data,self.data_dict[mlower])

		return

	def test_initial_retrieve(self):
		for m in MODELS:
			print 'Checking retrieve on %s...'%m
			self.retrieve(m, m.lower()+'s',m.lower())

	
	def test_update(self):
		for m in MODELS:
			print 'Checking update on %s...'%m
			first = self.data_dict[m.lower()][0]['pk']
			self.update(m, m.lower()+'s',int(first))
	
	def test_delete(self):
		for m in MODELS:
			print 'Checking delete on %s...'%m
			first = self.data_dict[m.lower()][0]['pk']
			self.delete(m, m.lower()+'s',int(first))

	def test_create(self):
		for m in MODELS:
			print 'Checking create on %s...'%m
			first = self.data_dict[m.lower()][0]
			self.create(m, m.lower()+'s',first)

