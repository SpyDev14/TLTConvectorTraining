from django.forms 			import Form, ModelForm
from django.views 			import generic

from core.models.general 	import Page
from core.models.bases 		import BaseRenderableModel
from core.views.mixins 		import PageInfoMixin, ConcretePageMixin
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
