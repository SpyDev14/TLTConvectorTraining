from django.contrib.sitemaps 	import Sitemap, GenericSitemap
from django.urls 				import reverse

from core.models.general 	import Page
from core.models.bases 		import BaseRenderableModel
from shared.reflection 		import get_subclasses

class DebugSitemap(Sitemap):
	def items(self):
		return Page.objects.all()

	def location(self, obj: Page):
		return reverse('debug-repr', args=[obj.slug])
