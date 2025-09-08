from core.views.bases import BasePageView

from django.shortcuts import get_object_or_404

# INFO: Связано проверкой в Page.clean() поля url_source
class GenericPageView(BasePageView):
	def get_page(self):
		url_path = self.kwargs['url_path']

		return get_object_or_404(self.model, url_source = url_path, is_generic_page = True)

	def get_template_names(self):
		return [self.object.template_name]


class DebugPageView(BasePageView):
	template_name = 'core/debug/page_repr.html'

	def get_page(self):
		return get_object_or_404(self.model, slug = self.kwargs['slug'])

	def get_template_names(self):
		return [self.template_name]
