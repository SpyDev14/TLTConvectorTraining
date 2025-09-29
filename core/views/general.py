from django.views.generic 	import DetailView
from django.shortcuts 		import get_object_or_404

from core.models.general 	import Page
from core.views.bases 		import BasePageView
from core.config 			import GENERIC_TEMPLATE

class _BasePageGenericView(BasePageView):
	# TODO: Почистить систему, в ходе развития
	# хочет вернуться к истокам
	def get_page(self):
		# Используем стандартный метод от Details
		# (забавно система сделана)
		return DetailView.get_object(self)

class GenericPageView(_BasePageGenericView):
	queryset = Page.objects.filter(is_generic_page=True)
	template_name_field = 'template_name'

class DebugPageView(_BasePageGenericView):
	template_name = 'core/debug/page_repr.html'
