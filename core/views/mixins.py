from typing import Any
import logging

from django.core.exceptions import ImproperlyConfigured
from django.shortcuts 		import get_object_or_404
from django.db.models 		import QuerySet

from core.models.general 	import Page
from core.models.bases 		import BaseRenderableModel


_logger = logging.getLogger(__name__)

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

# NOTE: Чтобы базовый класс не отвечал за стратегию получения
# объекта и можно было на чистой основе написать свою стратегию.
class ConcreteRenderableModelMixin:
	# Simple way
	renderable_model: type[BaseRenderableModel] | None = None
	renderable_slug: str | None = None

	# Advanced way
	renderable_queryset: QuerySet[BaseRenderableModel] | None = None

	def get_renderable_queryset(self):
		return self.renderable_queryset

	def get_renderable_object(self):
		queryset = self.get_renderable_queryset()

		if queryset and (self.renderable_slug or self.renderable_model):
			# NOTE: Может быть лучше вызывать исключение?
			_logger.warning(
				'Не указывайте и renderable_slug / renderable_model, и queryset одновременно, это '
				'не имеет смысла и может запутать других разработчиков.'
			)

		if not queryset:
			# Выбрал кратко и без повторения. Лаконично, но не слишком сложночитаемо.
			# Ps: все ведь шарят за МОРЖевой := оператор?
			if (no_slug := not self.renderable_slug) or (no_class := not self.renderable_model):
				both = no_class and no_slug
				raise ImproperlyConfigured(
					f"{'renderable_slug' if no_slug else ''} "
					f"{'и' if both else ''} "
					f"{'renderable_model' if no_class else ''} "
					f"не {'могут' if both else 'может'} быть пуст{'ы' if both else ''}"
					" при пустом queryset."
					" Либо установите значения в них, либо используйте queryset."
				)

			queryset = self.renderable_model.objects.filter(
				slug = self.renderable_slug
			)

		# NOTE: Осознанно ждём ошибку, если указанного объекта нет.
		return queryset.get()

# NOTE: Не придумал, как после рефакторинга переделать эти миксины, чтобы их можно было
# использовать и для Details и для List, как было раньше с get_page()
class ConcretePageMixin(ConcreteRenderableModelMixin):
	renderable_model = Page


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
