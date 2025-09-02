from typing import Any

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
	def get_page_info(self) -> BaseRenderableModel:
		raise NotImplementedError()

	def get_context_data(self, **kwargs):
		kwargs.update({
			'page_info': self.get_page_info()
		})
		return super().get_context_data(**kwargs)


# MARK: Page-details get_page() strategy
class ConcretePageMixin:
	page_slug: str | None = None

	def get_page(self):
		if not self.page_slug:
			raise ImproperlyConfigured('page_slug не может быть пуст!')
		return Page._default_manager.get(slug = self.page_slug)


class GenericPageMixin:
	url_kwarg_key: str = 'url_path'

	# Реализовал не самым лучшим образом, ранее просто всегда проверял
	# (защита от ситуации, где is_generic_page = False, но ей не присвоили
	# свой View и оно обрабатывается также через GenericPageView)
	check_is_generic_page: bool = True

	kwargs: dict[str, Any]

	def get_page(self):
		if not self.url_kwarg_key:
			raise ImproperlyConfigured('url_kwarg не может быть пуст!')
		url_path = self.kwargs[self.url_kwarg_key]

		additional_lookups = (
			{'is_generic_page': True}
			if self.check_is_generic_page
			else {}
		)
		return get_object_or_404(Page, url_path = url_path, **additional_lookups)
