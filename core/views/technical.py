from django.shortcuts 	import redirect
from django.views 		import View
from django.http 		import HttpResponse, HttpResponseNotFound

from core.models.singletons import SiteSettings
from shared 				import typename


# Решил выделить в отдельный модуль потому, что это технический View,
# нужный только для того, чтобы браузеры корректно получали favicon.
class FaviconView(View):
	def get(self, request):
		try:
			favicon_url = SiteSettings.get_solo().favicon.url
		except ValueError:
			return HttpResponseNotFound()

		return redirect(favicon_url)

class RobotsView(View):
	def get(self, request):
		return HttpResponse(
			SiteSettings.get_solo().robots_txt_content,
			content_type="text/plain"
		)

__all__ = [
	typename(FaviconView),
	typename(RobotsView)
]
