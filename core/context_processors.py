from typing import Callable

from django.conf 		import settings
from django.db.models 	import QuerySet

from solo.models 			import SingletonModel

from shared.string_processing.cases import camel_to_snake_case
from shared.reflection 				import typename
from core.models.singletons 		import *
from core.models.general 			import Page, ExtraContext
from core.models.bases 				import BaseRenderableModel

from business import models


def _singletons_to_context(singleton_classes: set[type[SingletonModel]]):
	return {
		camel_to_snake_case(typename(model)): model.get_solo()
		for model in singleton_classes
	}


def _model_qs_to_context_by_name[T](
		qs: QuerySet[T],
		key_field_name: str,
		name: Callable[[type[T]], str] | str = \
			lambda model_type: f"{camel_to_snake_case(typename(model_type))}s"
	) -> dict[str, T]:
	if not qs.exists():
		return {}

	if not isinstance(name, str):
		name: str = name(qs.model)

	key_field_value = getattr(qs.first(), key_field_name)

	if not isinstance(key_field_value, str):
		raise TypeError('Значение из указанного поля для ключа должно быть строкой')

	values_dict = {}
	for model in qs:
		key: str = getattr(model, key_field_name)
		values_dict[key.replace('-', '_')] = model
	return {name: values_dict}

def _base_renderable_model_qs_to_context(
		qs: QuerySet[BaseRenderableModel],
		key_field_name: str = 'slug',
		name: Callable[[type[BaseRenderableModel]], str] | str | None = None
	) -> dict[str, BaseRenderableModel]:
	return _model_qs_to_context_by_name(
		qs, key_field_name,
		*((name,) if name else ())
	)


# Создаёт нагрузку на БД, но я думаю, не такую сильную, так что нормально
# WARN: Нарушен OCP из SOLID, да и просто выглядит паршиво
# TODO: Реализовать систему с провайдерами
# https://chat.deepseek.com/a/chat/s/7cf344f9-d170-4542-9852-2badfc11257b
def global_context(request): return {
	'global': {
		**_singletons_to_context({
			SiteSettings,
			CompanyContacts
		}),
		**_model_qs_to_context_by_name(
			ExtraContext.objects.filter(page = None),
			'key', lambda model_type: camel_to_snake_case(typename(model_type))
		),

		**_base_renderable_model_qs_to_context(
			Page.objects
				.prefetch_related('extra_context_manager')
				.order_by('name'),
		),
		**_base_renderable_model_qs_to_context(
			models.Service.objects.all(),
		),
		**_base_renderable_model_qs_to_context(
			models.Category.objects.filter(parent = None),
			name = 'categories'
		)
	},
}

def debug_context(request): return {
	'DEBUG': settings.DEBUG,
}
