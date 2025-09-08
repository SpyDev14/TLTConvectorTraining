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


_make_default_name = lambda model: f"{camel_to_snake_case(typename(model))}s"
def _queryset_to_context(qs: QuerySet, name: str | None = None) -> dict[str, Iterable[Model]]:
	name = name or _make_default_name(qs.model)
	return {name: qs}

def _queryset_to_context_as_dict(
		qs: QuerySet,
		key_field_name: str,
		name: str | None = None) -> dict[str, dict[str, Model]]:
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
		name: str | None = None) -> dict[str, dict[str, BaseRenderableModel]]:
	return _queryset_to_context_as_dict(qs, 'slug', name)


def _singletons_provider():
	return {
		camel_to_snake_case(typename(model)): model.get_solo()
		# Определение списка SINGLETON_CLASSES находится ниже в модуле
		for model in SINGLETON_CLASSES_TO_GLOBAL_CONTEXT
	}

def _extra_context_provider():
	return _queryset_to_context_as_dict(
		ExtraContext.objects.filter(page = None), 'key',
		camel_to_snake_case(typename(ExtraContext))
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


# Я предпочёл явный список со всеми провайдерами вместо
# декоратора, чтобы код был более понятен для фронтендеров
# чтобы список доступных ресурсов был более очевидным
GLOBAL_CONTEXT_PROVIDERS: set[Callable[[], dict]] = {
	_singletons_provider,
	_extra_context_provider,
	_page_provider,
	_services_provider,
	_categories_provider,
}

SINGLETON_CLASSES_TO_GLOBAL_CONTEXT: set[type[SingletonModel]] = {
	SiteSettings,
	CompanyContacts
}

def global_context(request):
	context = {}
	for provider in GLOBAL_CONTEXT_PROVIDERS:
		context.update(provider())

	return {'global': context}
