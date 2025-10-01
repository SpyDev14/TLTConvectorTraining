from django.views.generic 	import DetailView

from core.models.general 	import Page
from core.views.bases 		import BasePageView

class GenericPageView(BasePageView):
	queryset = Page.objects.filter(is_generic_page=True)
	template_name_field = 'template_name'

	# TODO: Почистить систему
	def get_page(self):
		return DetailView.get_object(self)
