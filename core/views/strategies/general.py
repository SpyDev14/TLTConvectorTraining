from django.db.models import QuerySet

from core.models.bases 	import BaseRenderableModel
from .base 				import GetRenderableModelStrategy


class ConcreteRenderableModel(GetRenderableModelStrategy):
	def __init__(self, renderable_model_or_queryset: type[BaseRenderableModel] | QuerySet):
		# renderable_model
		pass


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
