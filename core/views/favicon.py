from django.shortcuts 	import redirect
from django.views 		import View

from core.models.singletons import SiteSettings

# Я решил даже для такого не использовать func-views
class Favicon(View):
	def get(self, request):
		favicon_url = SiteSettings.get_solo().favicon.url
		return redirect(favicon_url)
