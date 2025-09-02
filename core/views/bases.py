"""
Модуль с базовыми View для наследования.
Все эти View здесь потому, что не предполагается, что они
будут использоваться в urlpatterns напрямую.
"""
from typing import Any

from django.core.exceptions import ImproperlyConfigured
from django.db.models 		import QuerySet
from django.forms 			import Form, ModelForm
from django.views 			import generic

from core.models.general 	import Page
from core.models.bases 		import BaseRenderableModel
from core.views.mixins 		import *

from shared.string_processing 	import camel_to_snake_case
from shared.reflection 			import typename

# NOTE: Вместо миксинов я бы использовал паттерн стратегии, но т.к в базовых django
# классах используют миксины, я сделал в том же стиле.
# Ну честно, явная композиция + стратегия по интерфейсу здесь смотрелись бы куда лучше,
# как мне кажется.

def _make_context_name(obj: object | type) -> str:
	return camel_to_snake_case(typename(obj))

# MARK: BRM-detail views
# Для страниц статей (Article), товара (Product) и т.д
class BaseRenderableDetailView(PageInfoMixin, generic.DetailView):
	"""
	Базовый View для объектов, которые будут иметь свои detail-страницы.
	Добавляет информацию о странице через PageInfoMixin, и передаёт объект по названию модели
	в snake_case формате. В остальном работает как обычный DetailView.
	"""

	# Разработчики Django устанавливают object в get()
	# через setattr, спасибо -_-
	object: BaseRenderableModel
	# Не устанавливаю None т.к оно под капотом ожидает, что object будет
	# установлен в get через setattr, и либо атрибут будет, либо его не будет.
	# Разработчики конечно молодцы, спасибо им, что тут скажешь.

	def get_page_info(self):
		return self.object

	# Чтобы на страницах по типу atricle_detail.html обращались к article,
	# а не к object. Тем не менее, object остаётся в контексте.
	def get_context_object_name(self, obj):
		return _make_context_name(obj)

# MARK: └ Page-detail views
# View для страниц Page (о нас, политика приватности, главная (как родительская View), и так далее)
class BasePageView(BaseRenderableDetailView):
	"""
	Базовый View для страниц `Page` которые не отображают другие модели через список
	(о нас, главная, политика приватности), требует реализации метода `get_page()`.
	Отличается от `BaseRenderableDetailView` тем, что сразу указанно, что работает с моделью
	`Page`, а также есть место под метод получения объекта `Page`, для обеспечения одинакового
	интерфейса с `PageBasedListView`.
	"""
	object: Page # уточняем аннотацию
	model = Page

	# Для совместимости
	def get_page(self) -> Page:
		raise NotImplementedError('Должно быть реализовано в дочернем классе!')

	def get_object(self, queryset = None):
		return self.get_page()

	def get_template_names(self):
		if self.template_name:
			return [self.template_name]
		return [self.object.template_name]

# Для удобства
class ConcretePageView(
	ConcretePageMixin,
	BasePageView
): pass


class PageWithFormView(ConcretePageView, generic.edit.FormMixin, generic.edit.ProcessFormView):
	"""
	Работает так, как вы и ожидаете - BasePageDetailView, но с form в контексте.
	Указываете form_class, success_url и оно добавляет форму на страницу,
	а при успехе делает редирект на указанный url.

	Если это ModelForm - выполнит `form.save()`, иначе требуется явное
	переопределение form_valid (по умолчанию ничего не делает и просто редиректит).
	"""
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super().post(request, *args, **kwargs)

	def form_valid(self, form: Form):
		if isinstance(form, ModelForm):
			form.save()
		return super().form_valid(form)


# MARK: BRM-Based List views
class RenderableModelBasedListView(PageInfoMixin, generic.ListView):
	object_list: QuerySet | Any
	based_object_context_name: str | None = None

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.renderable_object: BaseRenderableModel | None = None

	def get_renderable_object(self):
		raise NotImplementedError('Должно быть реализовано в дочернем классе!')

	def get_page_info(self):
		return self.renderable_object

	# Нейминг супер, почему не ...objectS_name() ??! или ..._objects_list_name() ???
	# Переопределение базового метода
	def get_context_object_name(self, object_list):
		return (
			self.context_object_name
			or f"{_make_context_name(object_list.model)}s"
		)

	def get_based_object_context_name(self) -> str:
		return (
			self.based_object_context_name
			or _make_context_name(self.renderable_object)
		)

	def get_context_data(self, **kwargs):
		context: dict = super().get_context_data(**kwargs)

		context.update({
			self.get_based_object_context_name(): self.renderable_object,
			'based_object': self.renderable_object
		})

		return context

	def get(self, request, *args, **kwargs):
		self.renderable_object = self.get_renderable_object()
		return super().get(request, *args, **kwargs)

class ConcreteRenderableModelBasedListView(
	ConcreteRenderableModelMixin,
	RenderableModelBasedListView
): pass


class PageBasedListView(ConcreteRenderableModelBasedListView):
	"""
	Базовый View для List-страниц, где Page выступает в роли основы.
	Изначально, я думал делать всё через PageDetail View, но у ListView много
	логики для работы со списком, поэтому так.

	Суть этого View в том, что это стандартный ListView, но с присобаченным объектом
	page для передачи информации о странице который доступен по тому же ключу, что
	и в Page Details (информация о странице в `page_info`, объект Page в `page`).
	"""
	renderable_model = Page
