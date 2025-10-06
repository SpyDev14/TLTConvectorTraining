from django.core.exceptions import ImproperlyConfigured
from django.forms 			import Form, ModelForm
from django.views 			import generic

from core.models.general 	import Page
from core.models.bases 		import BaseRenderableModel
from core.views.mixins 		import PageInfoMixin
from core.config 			import GENERIC_TEMPLATE

from .make_context_name 	import make_context_name


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
		return make_context_name(obj)

	def get_template_names(self):
		names = super().get_template_names()

		# Template по умолчанию
		names.append(GENERIC_TEMPLATE.MODEL_DETAIL)
		return names

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

	# Специализированный метод для получения объекта страницы,
	# т.к это не "DetailView", а view для отображения страницы.
	# Ранее был нужен для миксиновой совместимости с PageBasedListView-s,
	# но сейчас оставлен для лучшей семантики.
	# NOTE: Может всё-таки убрать?
	# Должно быть переопределено в дочернем классе.
	def get_page(self) -> Page:
		raise NotImplementedError('Должно быть реализовано в дочернем классе!')

	def get_object(self, queryset = None):
		return self.get_page()

	def get_template_names(self):
		names = super().get_template_names()

		# Template по умолчанию (предпоследний)
		names.insert(len(names)-1, GENERIC_TEMPLATE.PAGE)
		return names

class ConcretePageView(BasePageView):
	page_slug: str | None = None

	def get_page(self):
		if not self.page_slug:
			raise ImproperlyConfigured('page_slug не может быть пуст!')
		return Page._default_manager.get(slug = self.page_slug)

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
