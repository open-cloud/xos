#from code.models import Slice

class SliceDeleter:
	model='Slice'

	def call(self, pk):
		s = Slice.objects.get(pk=pk)

		# Proceed with delete
