from django.db.models.signals 	import post_save
from django.template.response 	import TemplateResponse
from django.views.generic 		import TemplateView
from django.template 			import Template, RequestContext
from django.shortcuts 			import render
from django.dispatch 			import receiver
from django.http 				import HttpResponse
from django.urls 				import path

from core.models import Page

# TODO: Я напишу своё решение на основе обычного view, и частично TemplateView,
# т.к TemplateView здесь как-то не очень смотрится.
class BasePageView(TemplateView):
	page_slug: str  | None = None
	page:      Page | None = None

	def __init_subclass__(cls):
		if not cls.page_slug and not cls.page:
			raise ValueError(
				'Page slug and page cannot be empty both! Set variable value in an child classes '
				'or in **init_kwargs!'
			)

		if not cls.page:
			cls.page = Page.objects.get(slug = cls.page_slug)

		# Я решил не обрабатывать pre_delete т.к пускай нужно будет
		# перезапустить сервер для такого, с возвратом H404 это будет выглядеть не очень.
		@receiver(post_save, sender = Page)
		def on_page_save(instance: Page, created: bool, **kwargs):
			if created: return
			if instance.pk == cls.page.pk:
				cls.page = instance

		cls.template_name = cls.page.template_name

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['page'] = self.page
		return context

	@classmethod
	def as_path(cls):
		return path(cls.page.url_path, cls.as_view(), cls.page.url_name)

def dbg_view(request, url_path):
	content = """
{% extends 'base.html' %}

{% block content %}
url_path = {{ url_path }}
{% endblock content %}
"""
	context = RequestContext(request, {'url_path': url_path, 'page': {'verbose_name': 'DBG'}})
	template = Template(content)
	return HttpResponse(template.render(context))


