from typing import Callable, Iterable

from django.conf 		import settings
from django.db.models 	import QuerySet, Model

from solo.models 			import SingletonModel

from shared.string_processing.cases import camel_to_snake_case
from shared.reflection 				import typename
from core.models.singletons 		import *
from core.models.general 			import Page, ExtraContext
from core.models.bases 				import BaseRenderableModel

from business import models as models
from business import models as business


debug_context = lambda _: {'DEBUG': settings.DEBUG}

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

	if not isinstance(name, str):
		name: str = name(qs.model)

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


# WARN: Нарушен OCP из SOLID, да и просто выглядит паршиво
def __global_context_legacy(request): return {
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
			Page.objects.order_by('name'),
		),
		**_base_renderable_model_qs_to_context(
			models.Service.objects.all(),
		),
		**_base_renderable_model_qs_to_context(
			models.Category.objects.filter(parent = None),
			name = 'categories'
		),
		'recommended': {
			**_base_renderable_model_qs_to_context(
				models.Category.objects.recommended(),
				name = 'categories'
			),
		}
	},
}
global_context = __global_context_legacy


_make_default_name = lambda model: camel_to_snake_case(typename(model))

def _queryset_to_context(qs: QuerySet, name: str | None) -> dict[str, Iterable[Model]]:
	name = name or _make_default_name(qs.model)
	return {name: qs}

def _queryset_to_context_as_dict(
		qs: QuerySet, key_field_name: str,
		name: str | None) -> dict[str, dict[str, Model]]:
	name = name or _make_default_name(qs.model)

	context = {}
	for item in qs:
		key = getattr(item, key_field_name)
		if not isinstance(key, str): raise TypeError
		key = key.replace('-', '_')
		context[key] = item

	return {name: context}

def _base_renderable_model_qs_to_context_as_dict(
		qs: QuerySet[BaseRenderableModel],
		name: str | None) -> dict[str, dict[str, BaseRenderableModel]]:
	return _queryset_to_context_as_dict(qs, 'slug', name)


def _singletons_provider():
	return {
		camel_to_snake_case(typename(model)): model.get_solo()
		# Определение списка SINGLETON_CLASSES находится ниже в модуле
		for model in SINGLETON_CLASSES_TO_GLOBAL_CONTEXT
	}

def _extra_context_provider():
	return _queryset_to_context_as_dict(
		ExtraContext.objects.filter(page = None), 'key'
	)

def _page_provider():
	return _base_renderable_model_qs_to_context_as_dict(
		Page.objects.order_by('name')
	)

def _services_provider():
	return _queryset_to_context(
		business.Service.objects.all()
	)

def _categories_provider():
	return _queryset_to_context(
		business.Category.objects.root_nodes(),
		'categories'
	)

def _recommended_provider():
	return {
		'recommended': _queryset_to_context(
			business.Category.objects.recommended(),
			'categories'
		)
	}


# Я предпочёл явный список со всеми провайдерами вместо
# декоратора, чтобы код был более понятен для фронтендеров
# чтобы список доступных ресурсов был более очевидным
GLOBAL_CONTEXT_PROVIDERS: set[Callable[[], dict]] = {
	_singletons_provider,
	_extra_context_provider,
	_page_provider,
	_services_provider,
	_categories_provider,
	_recommended_provider
}

SINGLETON_CLASSES_TO_GLOBAL_CONTEXT: set[type[SingletonModel]] = {
	SiteSettings,
	CompanyContacts
}

def _global_context_new(request):
	context = {}
	for provider in GLOBAL_CONTEXT_PROVIDERS:
		context.update(provider())

	return context

# global_context = _global_context_new
