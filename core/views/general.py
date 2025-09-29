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
	# Если забыть указать is_generic_page - всё равно не покажет
	# not generic страницу с ошибкой [Errno 13] Permission denied.
	# Поле темплейта в этом кейте должно быть пустым => делает
	# неправильный путь и пытается открыть папку как файл))) Надёжно!
	queryset = Page.objects.filter(is_generic_page=True)

	def get_template_names(self):
		return [self.object.template_name, GENERIC_TEMPLATE.PAGE]

class DebugPageView(_BasePageGenericView):
	template_name = 'core/debug/page_repr.html'
