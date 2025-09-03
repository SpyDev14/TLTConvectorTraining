"""
Модуль с базовыми View для наследования.
Все эти View здесь потому, что не предполагается, что они
будут использоваться в urlpatterns напрямую.
"""
from typing import Any
import logging

from django.core.exceptions import ImproperlyConfigured
from django.db.models 		import QuerySet
from django.forms 			import Form, ModelForm
from django.views 			import generic

from core.models.general 	import Page
from core.models.bases 		import BaseRenderableModel
from core.views.mixins 		import PageInfoMixin, ConcretePageMixin
from core.config 			import GENERIC_TEMPLATE

from shared.string_processing 	import camel_to_snake_case
from shared.reflection 			import typename


_logger = logging.getLogger(__name__)

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
	# через setattr, спасибо =_=
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

	# Изначально было нужно для общего интерфейса с PageBasedListView, но после
	# рефакторинга былые миксины не задумываются для использования совместно с
	# BRM-Based List View, но переносить всё на стандартный get_object я не хочу
	# т.к он вторым аргументом может принимать qs, что мне совсем не нужно, и
	# стандартный метод получения object по pk, slug и т.д мне тоже не подходит
	# поэтому вместо повсеместного добавления qs вторым необязательным аргументом
	# и вызовом NotImplementedError в get_object этого класса решаю оставить так.

	# Если в будущем потребуется базовый функционал на основе get_object - это
	# можно будет легко изменить.
	def get_page(self) -> Page:
		raise NotImplementedError('Должно быть реализовано в дочернем классе!')

	def get_object(self, queryset = None):
		return self.get_page()
	
	def get_template_names(self):
		names = super().get_template_names()
		
		# Template по умолчанию
		names.append(GENERIC_TEMPLATE.PAGE)
		return names

# Для удобства; подключаю стратегию получения page отдельно, чтобы не засорять
# базовый класс.
class ConcretePageView(
	ConcretePageMixin,
	BasePageView
): pass

# Все страницы с формой будут использовать конкретную страницу указываемую в коде,
# врядли в скором будущем появится функционал добавления таких страниц через админку.
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
# Реализация get_renderable_object находится сразу здесь потому, что не планируется,
# что она будет координально отличаться в базовых классах, пока требуется чтобы всегда
# была указана конкретная страница.

# В будущем, по необходимости, это можно будет исправить.
# Если будет решено также из вне указывать стратегию получения объекта, то я бы
# полноценно реализовал паттерн "стратегия" через объекты типа Callable[[View], BaseRenderableObject],
# подходящих и для BRM-Detail, и для BRM-List.
# Подходят под такую аннотацию функции, лямбды и классы с __call__.
# Сложные, параметризируемых стратегии с внутренним состоянием можно реализовать
# через классы, передавая параметры через конструктор, или можно использовать
# фабричные функции с замыканиями - вариантов уйма.

# Что-то вида (для аннотации):
# GetRenderableObjectStrategy = Callable[[View], BaseRenderableObject]
# Подробнее (да, это только для меня):
# https://chat.deepseek.com/a/chat/s/37ff20b2-3299-4f23-8778-7592e06a47cf

# Ps: писал в нерабочее время

class RenderableModelBasedListView(PageInfoMixin, generic.ListView):
	# TODO: добавить docstring
	object_list: QuerySet | Any
	based_object_context_name: str | None = None

	# Simple way
	renderable_model: type[BaseRenderableModel] | None = None
	renderable_slug: str | None = None

	# Advanced way
	renderable_queryset: QuerySet[BaseRenderableModel] | None = None

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.renderable_object: BaseRenderableModel | None = None

	def get_renderable_queryset(self) -> QuerySet:
		queryset = self.renderable_queryset

		# Все проверки находятся здесь, а не в __init_subclass__() потому, что
		# эти атрибуты потенциально могут быть установлены через **initkwargs в
		# методе .as_view(), хотя я такое не одобряю, но так в django.

		# Если пробуют simple и advanced способом одновременно, то предупреждаем о логической ошибке
		# (но игнорируем установленную модель)
		if queryset is not None and self.renderable_slug:
			# NOTE: Может быть лучше вызывать исключение?
			_logger.warning(
				'Не указывайте и renderable_slug c renderable_model, и queryset одновременно, это '
				'не имеет смысла и может запутать других разработчиков. Метод через queryset имеет '
				'больший приоритет.'
			)

		if queryset is None:
			# Первое всегда будет проверено, второе - нет. Поэтому не использую
			# МОРЖевой оператор := там (or блок, внутренние оптимизации языка)
			if (no_class := not self.renderable_model) or not self.renderable_slug:
				# both
				if no_class and not self.renderable_slug:
					raise ImproperlyConfigured(
						'renderable_slug и renderable_model не могут быть пусты '
						'при пустом queryset. Либо установите значения в них, либо '
						'сразу используйте свой queryset.'
					)
				else:
					missing_var_name = 'renderable_model' if no_class else 'renderable_slug'
					raise ImproperlyConfigured(
						f'{missing_var_name} не может быть пуст при пустом queryset. Либо установите'
						' значение, либо сразу используйте свой queryset.'
					)

			queryset = self.renderable_model._default_manager.filter(
				slug = self.renderable_slug
			)

		return queryset.all()

	def get_renderable_object(self):
		queryset = self.get_renderable_queryset()

		# Осознанно ждём ошибку, если указанного объекта нет.
		return queryset.get()

	def get_page_info(self):
		return self.renderable_object

	#                                   v                          vvvvvv
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


class PageBasedListView(RenderableModelBasedListView):
	# TODO: Добавить docstring

	renderable_model = Page
