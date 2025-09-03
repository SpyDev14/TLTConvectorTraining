from core.views.bases 		import BasePageView
from core.views.mixins 		import GenericPageMixin

# INFO: Связано хардкод проверкой в Page.clean() поля url_path
class GenericPageView(GenericPageMixin, BasePageView):
	def get_template_names(self):
		return [self.object.template_name]

class DebugPageView(GenericPageMixin, BasePageView):
	template_name = 'core/debug/page_repr.html'
	check_is_generic_page = False

	def get_template_names(self):
		return [self.template_name]
