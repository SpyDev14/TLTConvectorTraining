from django.shortcuts 	import redirect
from django.views 		import View

from core.models.singletons import SiteSettings


# Решил выделить в отдельный модуль потому, что это технический View,
# нужный только для того, чтобы браузеры корректно получали favicon.
class FaviconView(View):
	def get(self, request):
		favicon_url = SiteSettings.get_solo().favicon.url
		return redirect(favicon_url)
