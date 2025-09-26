from functools 	import cached_property
from itertools 	import chain
from datetime 	import datetime

from django.contrib.sitemaps 	import Sitemap, GenericSitemap
from django.db.models 			import Max, QuerySet
from django.urls 				import reverse

from core.models.general 	import Page
from core.models.bases 		import BaseRenderableModel
from shared.reflection 		import get_subclasses

class DebugSitemap(Sitemap):
	def items(self):
		return Page.objects.all()

	def location(self, obj: Page):
		return reverse('debug-repr', args=[obj.slug])

class GenericBaseRenderableModelsSitemap(Sitemap):
	def __init__(self):
		# Преобразуем генератор в tuple, иначе мо нему можно
		# будет проитерироваться только один раз!
		self._brm_subsubmodels = tuple(
			submodel for submodel in
			get_subclasses(BaseRenderableModel)
			if not submodel._meta.abstract
		)
		super().__init__()

	def items(self):
		# Разрабов надо избить, на кой хер они прикрутили ПАГИНАЦИЮ к SITEMAP!!!!
		# и из-за пагинатора, я не могу вернуть итератор по qs, мне нужен "SupportsLen".
		# Козлы.
		return tuple(
			submodel.get_sitemap_queryset()
			for submodel in self._brm_subsubmodels
		)

	def lastmod(self, obj: BaseRenderableModel):
		return obj.last_modified_time

	def get_latest_lastmod(self):
		latest = None

		for model in self._brm_subsubmodels:
			max_lastmod: datetime | None = model.objects.aggregate(
				max_lastmod = Max('last_modified_time')
			)['max_lastmod']
			if not max_lastmod: continue

			if latest < max_lastmod or latest is None:
				latest = max_lastmod

		return latest
