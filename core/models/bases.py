from typing import Any

from django.core.exceptions 			import ImproperlyConfigured
from django.urls 						import reverse, NoReverseMatch
from django.db 							import models

from shared.seo.og 						import OgType
from core.models.singletons 			import SiteSettings

# TODO: Добавлять в html_title название сайта к исходному html_title
# TODO: Добавить метод get_parent_object в BRM возвращающий BRM объект,
# считающийся родительским для этого объекта.
# NOTE: Название кал, у кого-то есть идеи как это можно переименовать?
class BaseRenderableModel(models.Model):
	"""
	Базовая модель для всех моделей, у которых будут свои detail (и опционально
	list) страницы: статьи, товары, услуги, категории и подобные, а также является
	базовой для `Page`, которая используется для простых страниц по типу `О нас` или
	`Политика приватности` (просто текст), а также как основа для list страниц других
	`BaseRenderableModel`: `Блог`, `Услуги` и т.д.<br>
	Работает совместо со специализированными view, которые вы можете
	найти в папке `core/views/bases/`.

	Содержит поля для SEO, для генерации url, методы получения связанных url,
	**автоматически добавляется в sitemap** (наследники).
	"""
	# см. get_absolute_url()
	# Под редкое переопределение в подклассах
	_url_name: str | None = None
	_url_kwarg_name: str = 'slug'

	name = models.CharField('Название', max_length = 64,
		help_text = 'Указывайте человеко-читаемый текст. По умолчанию также '
		'используется для HTML Title и H1.')
	# slug тут не совсем к месту т.к это про получение объекта на основе запроса,
	# но опустим этот момент, это слишком мелкая деталь.
	slug = models.SlugField(max_length = 128, unique = True)
	h1 = models.CharField('H1 Заголовок', max_length = 127, blank = True,
		help_text = 'По умолчанию для H1 используется Name.')
	html_title = models.CharField('HTML Title', max_length = 128, blank = True,
		help_text = 'По умолчанию для HTML Title используется Name.')
	add_sitename_to_html_title = models.BooleanField('Добавить название сайта к HTML Title?', default=True)
	html_description = models.TextField('HTML Description', blank = True)
	last_modified_time = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True

	def __str__(self):
		return self.name

	def get_h1(self) -> str:
		return self.h1 or self.name

	def get_html_title(self) -> str:
		sitename = SiteSettings.get_solo().site_name
		return (
			(self.html_title or self.name)
			+
			(f" | {sitename}" if self.add_sitename_to_html_title else '')
		)

	def get_html_description(self) -> str:
		return self.html_description

	# Необходимо указать в дочернем классе, но можно оставить по умолчанию
	og_type: OgType = OgType.WEBSITE

	@property
	def og_title(self) -> str:
		return self.get_html_title()

	@property
	def og_description(self) -> str | None:
		return self.get_html_description()

	@property
	def og_image_url(self) -> str | None:
		return None

	def _get_microdata(self) -> dict[str, Any]:
		"""Под переопределение, возвращайте здесь нужный объект с данными"""
		raise NotImplementedError('Переопределите этот метод в дочернем классе!')

	def get_full_microdata(self) -> dict[str, Any]:
		"""Возвращает self._get_microdata() с подставленным значением по умолчанию"""
		return {
			'@context': 'https://schema.org',
			**self._get_microdata()
		}

	def get_absolute_url(self) -> str:
		default_url_name = f'{self._meta.model_name}-detail'
		url_name = self._url_name or default_url_name

		try:
			return reverse(url_name, kwargs = {self._url_kwarg_name: self.slug})
		except NoReverseMatch:
			raise ImproperlyConfigured(
				'Вы не настроили get_absolute_url()! Настройте, либо переопределите базовый метод.'
			)

	def get_admin_url(self):
		return f'/admin/{self._meta.app_label}/{self._meta.model_name}/{self.pk}/change/'

	@classmethod
	def get_sitemap_queryset(cls):
		return cls.objects.all()
