"""
Модуль с базовыми View для наследования.
"""

from typing import Callable, Self

from django.core.exceptions import ImproperlyConfigured
from django.shortcuts 		import get_object_or_404, redirect
from django.db.models 		import Model
from django.forms 			import Form, ModelForm
from django.views 			import generic
from django.http 			import HttpRequest

from core.models.general 	import Page
from core.models.bases 		import BaseRenderableModel
from core.views.mixins 		import PageInfoMixin, ConcretePageMixin

from shared.string_processing 	import camel_to_snake_case
from shared.reflection 			import typename

def _make_context_name(obj: object | type) -> str:
	return camel_to_snake_case(typename(obj))

# Для страниц статей, товара и т.д
class BaseRenderableDetailView(PageInfoMixin, generic.DetailView):
	"""
	Базовый View для объектов, которые будут иметь свои detail-страницы.
	Добавляет информацию о странице через PageInfoMixin, и передаёт объект по названию модели
	в snake_case формате. В остальном работает как обычный DetailView.
	"""
	# Разработчики Django клали на аннотацию, устанавливают
	# object в get через setattr, спасибо -_-
	object: BaseRenderableModel
	# Не устанавливаю None т.к оно под капотом ожидает, что object будет
	# установлен в get через setattr, и либо атрибут будет, либо его не будет.
	# Разработчики конечно молодцы, спасибо им, что тут скажешь.

	def get_page_info(self):
		return self.object

	def get_context_object_name(self, obj):
		return _make_context_name(obj)


# View для страниц Page
class BasePageView(BaseRenderableDetailView):
	"""
	Базовый View для страниц Page которые не отображают другие модели через список
	(о нас, главная, политика приватности), требует реализации метода get_page.
	Отличается от BaseRenderableDetailView тем, что сразу указанно, что работает с моделью
	Page, а также есть место под метод получения объекта Page, для обеспечения одинакового
	интерфейса с BasePageBasedListView.

	Сочетается со стандартными django generic views, но лучше смотрите "на месте", так как
	некоторые стандартные django generic view конфликтуют друг с другом, этот - наследник DetailView.
	"""
	object: Page # уточняем аннотацию
	model = Page

	def get_page(self) -> Page:
		raise NotImplementedError('Используйте готовый mixin, или напишите свою логику.')

	def get_object(self, queryset = None):
		return self.get_page()

	def get_template_names(self):
		return [self.object.template_name]


class FormPageView(BasePageView, generic.edit.FormMixin, generic.edit.ProcessFormView):
	"""
	Работает так, как вы и ожидаете - BasePageDetailView, но с form в контексте.
	Указываете form_class, success_url и оно добавляет форму на страницу,
	а при успехе делает редирект на указанный адрес.

	Если это ModelForm - выполнит `form.save()`.
	"""
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super().post(request, *args, **kwargs)

	def form_valid(self, form):
		if isinstance(form, ModelForm):
			form.save()
		return super().form_valid(form)


class BasePageBasedListView(PageInfoMixin, generic.ListView):
	"""
	Базовый View для List-страниц, где Page выступает в роли основы.
	Изначально, я думал делать всё через PageDetail View, но у ListView много
	логики для работы со списком, поэтому так.

	Суть этого View в том, что это стандартный ListView, но с присобаченным объектом
	page для передачи информации о странице который доступен по тому же ключу, что
	и в Page Details (информация о странице в `page_info`, объект Page в `page`).
	"""

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.page_object: Page | None = None

	def get_page(self) -> Page:
		raise NotImplementedError('Используйте готовый mixin, или напишите свою логику.')

	def get_page_info(self):
		return self.page_object

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context[_make_context_name(self.page_object)] = self.page_object
		return context

	def get(self, request, *args, **kwargs):
		self.page_object = self.get_page()
		return super().get(request, *args, **kwargs)


# Чтобы не наследоваться каждый раз от ConcretePageMixin
class ConcretePageView(ConcretePageMixin, BasePageView):
	pass

class ConcretePageBasedListView(ConcretePageMixin, BasePageBasedListView):
	pass
