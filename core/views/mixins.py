from django.core.exceptions import ImproperlyConfigured
from django.shortcuts 		import get_object_or_404

from core.models.general 	import Page
from core.models.bases 		import BaseRenderableModel



class PageInfoMixin:
	"""
	Добавляет page_info в контекст.
	Обычно, это просто дублирует объект в контекстный ключ page_info.
	Обращайтесь к данным о странице через page_info, а не через сам объект!

	Требует:
	- Этот класс имеет реализацию get_context_data
	"""
	def __init_subclass__(cls):
		super().__init_subclass__()

		if not hasattr(cls, 'get_context_data'):
			raise AttributeError(
				'Этот mixin расчитан только на работу с классами, '
				'реализующими метод get_context_data.'
			)

	def get_page_info(self) -> BaseRenderableModel:
		raise NotImplementedError()

	def get_context_data(self, **kwargs):
		kwargs.update({
			'page_info': self.get_page_info()
		})
		return super().get_context_data(**kwargs)


class ConcretePageMixin:
	"""
	Миксин переопределяющий получение объекта
	страницы на get_object_or_404 по заранее прописанному во View slug.

	Требует:
	- Это подкласс BasePageView
	"""
	page_slug: str | None = None

	def get_page(self):
		if not self.page_slug:
			raise ImproperlyConfigured('page_slug не может быть пуст')
		return get_object_or_404(Page, slug = self.page_slug)


# Врядли будут где-то использовать также, как и ConcretePageMixin,
# скорее задел на будущее с GenericForeginKey на модели Page чтобы
# добавлять страницы со списком моделей через админку.
# В прочем, я бы это и сделал, если бы не было проблемы с кастомными
# QuerySet-s для большинства таких view.
class GenericPageMixin:
	url_kwarg_key: str = 'url_path'
	kwargs: dict

	def get_page(self):
		if not self.url_kwarg_key:
			raise ImproperlyConfigured('url_kwarg не может быть пуст')
		url_path = self.kwargs[self.url_kwarg_key]
		return get_object_or_404(Page, url_path = url_path, is_generic_page = True)
