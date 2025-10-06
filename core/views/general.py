from django.views.generic 	import DetailView

from core.models.general 	import Page
from core.views.bases 		import BasePageView

class GenericPageView(BasePageView):
	queryset = Page.objects.filter(is_generic_page=True)
	template_name_field = 'template_name'

	# Выглядит странно, но тут суть в том, что стратегия получения
	# страницы здесь - как стратегия получения объекта у
	# стандартного DetailView
	def get_page(self):
		return DetailView.get_object(self)
