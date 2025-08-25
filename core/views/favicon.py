from django.shortcuts 	import redirect
from django.views 		import View

from core.models.singletons import SiteSettings


class FaviconView(View):
	def get(self, request):
		favicon_url = SiteSettings.get_solo().favicon.url
		return redirect(favicon_url)
