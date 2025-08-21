from django.shortcuts 	import get_object_or_404, redirect
from django.forms 		import ModelForm
from django.http 		import HttpRequest

from core.models.general 	import Page
from core.views 			import BasePageView


class ConcretePageView(BasePageView):
	page_slug: str | None = None

	def get_page_object(self):
		if not self.page_slug:
			raise ValueError(
				'page_slug не может быть пуст при методе получения Page через page_slug'
			)
		return get_object_or_404(Page, slug = self.page_slug)


class GenericPageView(BasePageView):
	def get_page_object(self):
		url_path = self.kwargs['url_path']
		return get_object_or_404(Page, url_path = url_path, is_generic_page = True)


class FormPageView(ConcretePageView):
	form_class: type[ModelForm] | None = None
	success_url: str | None = None

	def get_success_response(self):
		if not self.success_url:
			raise ValueError("success_url не может быть пуста, если вы используете стандартный метод.")
		return redirect(f'/{self.success_url}')

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		if not self.form_class:
			raise ValueError('form_class не может быть пуст.')
		if self.success_url.startswith('/'):
			raise ValueError('success_url не должно начинаться на /')

	def get_context(self, *, page, **kwargs):
		kwargs.setdefault('form', self.form_class())
		return super().get_context(page = page, **kwargs)

	def post(self, request: HttpRequest):
		form = self.form_class(request.POST)

		if form.is_valid():
			form.save()
			return self.get_success_response()

		page = self.get_page_object() # переопределяем vvvv
		context = self.get_context(page = page, form = form)
		return self.render_to_response(page, context, status = 400)
